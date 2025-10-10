import os
import json
import random
import platform
import moviepy.config as mpc
import gc

from gtts import gTTS
# import pygame
# pygame.init()

from moviepy.editor import *

if platform.system() == "Windows":
    mpc.change_settings({
        "IMAGEMAGICK_BINARY": r"E:\\ImageMagick-7.1.2-Q16-HDRI\\magick.exe"
    })

os.makedirs("src/tts", exist_ok=True)
os.makedirs("src/outputs", exist_ok=True)

my_font = r"src/fonts/bold_font.ttf"

with open('would_you_rather.json', 'r') as f:
    data = json.load(f)
questions = data['questions']

# Load used_questions
if os.path.exists("src/used_questions.json"):
    with open("src/used_questions.json", "r") as f:
        used_questions = set(json.load(f))
else:
    used_questions = []

n = 5

available = [q for q in questions if q not in used_questions]
if len(available) < n:
    # ลบคำถามที่เคยใช้ทั้งหมด
    used_questions = []
    available = questions.copy()

selected_questions = random.sample(available, n)

backgrounds = ['src/template.png']

# Music
music_path = f"src/song/song.mp3"
try:
    music = AudioFileClip(music_path).volumex(0.2)
    print("Music loaded successfully")
except Exception as e:
    print(f"Music loading failed: {e}")
    music = None

clips = []
text_clips = []
audio_clips = []

# =============== Search IMG ========================

import re
import requests
import numpy as np 
from dotenv import load_dotenv
from PIL import Image
load_dotenv()


API_KEY = os.getenv("UNS_ACCESS")  # ใส่ Access Key ของ Unsplash

os.makedirs("src/imgs", exist_ok=True)

def search_image(query):
    if not API_KEY:
        print("Warning: Unsplash API Key not found")
        return None
    
    url = "https://api.unsplash.com/photos/random"
    params = {
        "query": query,
        "client_id": API_KEY,
        "orientation": "landscape"
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        print(resp.status_code, resp.text[:200])  # debug
        data = resp.json()
        if "urls" in data and "regular" in data["urls"]:
            return data["urls"]["regular"]
    except Exception as e:
        print(f"Search error: {e}")
    return None

def download_image(url, save_path):
    if not url:
        return None
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(url, stream=True, timeout=10, headers=headers)
        r.raise_for_status()  # Check status code
        
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        try:
            img = Image.open(save_path)
            img = img.convert("RGB")  # Convert to RGB
            img.verify()
            
            # Reopen for processing (verify closes the image)
            img = Image.open(save_path).convert("RGB")
            # Resize to reasonable dimensions
            img.thumbnail((800, 600), Image.LANCZOS)
            img.save(save_path, "JPEG", quality=85)
            return save_path
        except Exception as e:
            print(f"File image damages: {save_path} | remove and skip: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Cannot download file from {url}: {e}")
        return None
    
def get_keywords(text, max_words=5):
    text = re.sub(r'[^\w\s]', '', text)
    words = text.split()
    # Adjust
    keywords = [w for w in words if len(w) > 2]
    return ' '.join(keywords[:max_words])

def search_with_fallback(option):
    if not option.strip():
        return None
    query = get_keywords(option)
    print("Trying keyword search:", query)  # <-- debug
    url = search_image(query)
    if url:
        return url
    
    return search_progressive(option)

def search_progressive(option):
    words = option.split()
    n = 1
    while n <= len(words):
        # สร้างทุก combination ของ n คำต่อเนื่อง
        for start in range(len(words) - n + 1):
            query = ' '.join(words[start:start+n])
            url = search_image(query)
            if url:
                return url
        n += 1  
    return None  

def safe_imageclip(path, pos, start, duration, resize=0.5):
    if not path or not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGB")
        img = img.resize((int(img.width*resize), int(img.height*resize)), Image.LANCZOS)
        clip = ImageClip(np.array(img)).set_position(pos).set_start(start).set_duration(duration)
        return clip
    except Exception as e:
        print(f"Cannot load image {path}: {e}")
        return None

# Download images first
print("Starting image download...")
top_img_paths = []
bot_img_paths = []

for i, q in enumerate(selected_questions):
    print(f"Processing question {i+1}/{len(selected_questions)} for images...")
    try:
        if ' or ' in q:
            option1, option2 = q.split(' or ', 1)
        else:
            option1, option2 = q, ""

        # Top image
        top_img_path = f"src/imgs/top_image_{i}.jpg"
        url = search_with_fallback(option1)
        top_img_path = download_image(url, top_img_path)
        if top_img_path:
            print(f"Top image {i} downloaded: {top_img_path}")
        else:
            print(f"Top image {i} failed, skipped")
            top_img_path = None
        top_img_paths.append(top_img_path)

        # Bot image
        bot_img_path = f"src/imgs/bot_image_{i}.jpg"
        url = search_with_fallback(option2)
        bot_img_path = download_image(url, bot_img_path)
        if bot_img_path:
            print(f"Bot image {i} downloaded: {bot_img_path}")
        else:
            print(f"Bot image {i} failed, skipped")
            bot_img_path = None
        bot_img_paths.append(bot_img_path)

        # Small delay to avoid rate limiting
        import time
        time.sleep(0.5)

    except Exception as e:
        print(f"Image download error at question {i}: {e}")
        top_img_paths.append(None)
        bot_img_paths.append(None)

print("Image download completed. Creating video clips...")

#============================================================

#========================== Effects ========================

t = 0

def bounce_in(t, duration=0.5):
    """
    สร้าง bounce effect for text
    t: Current time
    duration: duration of animation
    """
    if t > duration:
        return 1.0
    
    # ใช้ easing function แบบ bounce
    progress = t / duration
    if progress < 0.363636:
        return 7.5625 * progress * progress
    elif progress < 0.727272:
        progress -= 0.545454
        return 7.5625 * progress * progress + 0.75
    elif progress < 0.909090:
        progress -= 0.818181
        return 7.5625 * progress * progress + 0.9375
    else:
        progress -= 0.954545
        return 7.5625 * progress * progress + 0.984375

def bounce_from_bottom(t):
    if t < 0.6:
        bounce_progress = bounce_in(t, 0.6)
        y_offset = (1 - bounce_progress) * 200  # เริ่มจากด้านล่าง
        return ('center', 1050 + y_offset)
    else:
        return ('center', 1050)
    
def animate_text_bounce(txt_clip, start_pos, bounce_duration=0.6):
    def position_func(t):
        if t < bounce_duration:
            progress = bounce_in(t, bounce_duration)
            y_offset = (1 - progress) * (-200)  # เริ่มจากบน
            return (start_pos[0], start_pos[1] + y_offset)
        return start_pos
    return txt_clip.set_position(position_func)

# IMAGES

def image_bounce_from_top(path, start_pos, start_time, duration, bounce_duration=0.6, resize=0.5):
    # load clip through safe_imageclip
    clip = safe_imageclip(path, start_pos, start_time, duration, resize)
    if not clip:
        return None
    
    def pos(t):
        if t < bounce_duration:
            progress = bounce_in(t, bounce_duration)
            y_offset = (1 - progress) * -200  # เริ่มจาก -200 px ด้านบน
            return (start_pos[0], start_pos[1] + y_offset)
        return start_pos

    return clip.set_position(pos)

def image_bounce_from_bottom(path, start_pos, start_time, duration, bounce_duration=0.6, resize=0.5):
    clip = safe_imageclip(path, start_pos, start_time, duration, resize)
    if not clip:
        return None
    
    def pos(t):
        if t < bounce_duration:
            progress = bounce_in(t, bounce_duration)
            y_offset = (1 - progress) * 200  # เริ่มจาก +200 px ด้านล่าง
            return (start_pos[0], start_pos[1] + y_offset)
        return start_pos
    
    return clip.set_position(pos)


#===========================================================

# =============== Create Video Clips ========================

def create():


    total_duration = 1

    choose_img_path = f"src/choose.jpg"

    intro_img = ImageClip(choose_img_path) \
    .resize((700,700)) \
    .set_position(('center', 'center')) \
    .set_start(0) \
    .set_duration(1)
    
    txt_choose = TextClip(
    "What would you choose?",
    fontsize=40,
    color='White',
    font=my_font,
    method='label',
    size=(600,50),
    align='center'
    ).set_position(('center',1000)).set_start(0).set_duration(1)

    #tts
    intro_txt = "What would you choose?"
    tts_choose_file = 'src/tts/choose_tts.mp3'
    tts_choose = gTTS(text=intro_txt, lang='en')
    tts_choose.save(tts_choose_file)
    audio_choose = AudioFileClip(tts_choose_file).fx(vfx.speedx, 1.25)
    audio_clips.append(audio_choose.set_start(0))

    

    for i, q in enumerate(selected_questions):
        print(f"Creating clips for question {i+1}/{len(selected_questions)}...")
        
        if ' or ' in q:
            option1, option2 = q.split(' or ', 1)
            option1, option2 = option1.strip(), option2.strip()
        else:
            option1, option2 = q, ""

        # TTS
        try:
            tts_file = f'src/tts/tts_{i}.mp3'

            tts = gTTS(text=q, lang='en')
            tts.save(tts_file)

            audio_clip = AudioFileClip(tts_file).fx(vfx.speedx, 1.25)
            print(f"TTS created for question {i+1}: {audio_clip.duration:.1f}s")
            
        except Exception as e:
            print(f"TTS error for question {i}: {e}")
            continue

        txt_main_dura = audio_clip.duration
        wait_before_percent = 3
        percent_duration = 1.5
        wait_after_percent = 0.2
        end_time = txt_main_dura + wait_before_percent + percent_duration + wait_after_percent

        audio_clips.append(audio_clip.set_start(total_duration))

        # FX sound
        try:
            fx_clip = AudioFileClip("src/sfx/clock-ticking.mp3").set_start(total_duration + txt_main_dura).set_duration(wait_before_percent).volumex(0.5)
            audio_clips.append(fx_clip)
        except Exception as e:
            print(f"FX sound error: {e}")

        try:
            fx_clip = AudioFileClip("src/sfx/ding.mp3").set_start(total_duration + txt_main_dura + wait_before_percent).set_duration(2).volumex(0.5)
            audio_clips.append(fx_clip)
        except Exception as e:
            print(f"FX sound error: {e}")

        num_ran = random.uniform(0.0, 100)

        # Text clips - keeping original positions and timing
        try:
            txt_top = TextClip(
                f"{option1}",
                fontsize=50, 
                color='white',
                font=my_font,
                method='caption',
                size=(700,100), 
                align='center'
            ).set_position(('center',65)).set_start(total_duration).set_duration(end_time)

            txt_top = animate_text_bounce(txt_top, ('center', 65), bounce_duration=0.6)

            txt_bot = TextClip(
                f"{option2}",
                fontsize=50,
                color='white',
                font=my_font,
                method='caption',
                size=(700,300),
                align='center'
            ).set_position(('center',1050)).set_start(total_duration).set_duration(end_time)

            txt_bot = txt_bot.set_position(bounce_from_bottom)
            
            txt_or = TextClip(
                "OR",
                fontsize=70,
                color='white',
                font=my_font,
                method='label',
                size=(700,100),
                align='center').set_position(('center',620)).set_start(total_duration).set_duration(end_time)
            
            txt_num1 = TextClip(
                f"{round(num_ran, 2)}%",
                fontsize=45,
                color="red" if round(num_ran, 2) < round(100.0 - round(num_ran, 2), 2) else "green",
                font=my_font,
                method="label",
                size=(300,100),
                align='center'
            ).set_position(('center',500)).set_start(total_duration + txt_main_dura + wait_before_percent).set_duration(percent_duration)
            
            txt_num2 = TextClip(
                f"{round(100.0 - round(num_ran, 2), 2)}%",
                fontsize=45,
                color="red" if round(100.0 - round(num_ran, 2), 2) < round(num_ran, 2) else "green",
                font=my_font,
                method="label",
                size=(300,100),
                align='center').set_position(('center',735)
            ).set_start(total_duration + txt_main_dura + wait_before_percent).set_duration(percent_duration)  # Fixed timing
            
        except Exception as e:
            print(f"Text clip creation error: {e}")
            continue
        
        # --- Debug TextClip ---
        for name, clip in [("txt_top", txt_top), ("txt_bot", txt_bot), ("txt_or", txt_or), ("txt_num1", txt_num1), ("txt_num2", txt_num2)]:
            if clip is None:
                print(f"[DEBUG] {name} is None for question {i}")
            else:
                print(f"[DEBUG] {name} created: duration={clip.duration}, position={clip.pos}")
        
        # --- Images with original positions ---
        top_clip = image_bounce_from_top(top_img_paths[i], ("center", 165), total_duration, end_time)
        if top_clip is None:
            top_clip = ColorClip(size=(10,20), color=(0,0,0)).set_position(("center",327)).set_start(total_duration).set_duration(end_time)

        bot_clip = image_bounce_from_bottom(bot_img_paths[i], ("center", 850), total_duration, end_time)
        if bot_clip is None:
            bot_clip = ColorClip(size=(10,20), color=(128,128,128)).set_position(("center",900)).set_start(total_duration).set_duration(end_time)

        # --- Debug ImageClip ---
        for name, path, clip in [("top_clip", top_img_paths[i], top_clip), ("bot_clip", bot_img_paths[i], bot_clip)]:
            if clip is None:
                print(f"[DEBUG] {name} is None! path={path}")
            else:
                print(f"[DEBUG] {name} created: duration={clip.duration}, size={clip.size}, position={clip.pos}")

        # Add clips if not None
        clips.extend([c for c in [top_clip, bot_clip] if c])
        text_clips.extend([txt_top, txt_bot, txt_or, txt_num1, txt_num2])

        total_duration += end_time
        
        # Force garbage collection after each question
        gc.collect()
        print(f"Question {i+1} completed. Total duration so far: {total_duration:.1f}s")

    print(f"\nAll clips created. Total duration: {total_duration:.1f}s")
    print("Creating background and final composition...")


    # Background clip
    try:
        bg_clip = ColorClip(size=(720,1280), color=(0,0,0)).set_start(0).set_duration(1)
        bg_clip = ImageClip("src/template.png").resize((720,1280)).set_start(1).set_duration(total_duration)
        print("Background loaded successfully")
    except Exception as e:
        print(f"Background error: {e}. Using black background.")
        bg_clip = ColorClip(size=(720,1280), color=(0,0,0)).set_duration(total_duration)

    print("Compositing video...")

    try:
        # Filter out None clips
        valid_clips = [txt_choose, intro_img] + [clip for clip in text_clips + clips if clip is not None]
        final_clip = CompositeVideoClip([bg_clip] + valid_clips)
        print(f"Video composition completed with {len(valid_clips)} clips")

        # ==== DEBUG INFO ====
        # print("\n[DEBUG] Clip information:")
        # for i, clip in enumerate([bg_clip] + valid_clips):
        #     try:
        #         print(f"[{i}] type={type(clip).__name__}, size={clip.size}, pos={clip.pos}, duration={clip.duration}")
        #     except Exception as e:
        #         print(f"[{i}] Error getting clip info: {e}")
        # print("=====================\n")

        # # Preview เฉพาะ BG + 2 text clip พอ (เร็วกว่า)
        # print("Previewing background + 2 text clips for debug...")
        # debug_clip = CompositeVideoClip([bg_clip] + valid_clips[:2])
        # debug_clip.preview(fps=5)
        # debug_clip.close()
        # ====================
        
        # Create final audio
        valid_audio_clips = [clip for clip in audio_clips if clip is not None]
        if music is not None:
            # Loop music to match video duration
            if music.duration < total_duration:
                music_looped = music.loop(duration=total_duration)
            else:
                music_looped = music.subclip(0, total_duration)
            valid_audio_clips.append(music_looped)
        
        if valid_audio_clips:
            final_audio = CompositeAudioClip(valid_audio_clips)
            final_clip = final_clip.set_audio(final_audio)
            print("Audio composition completed")
        
        print("Writing video file... This may take a while...")
        final_clip.write_videofile(
            "src/outputs/final.mp4",
            fps=24,
            threads=2,  # Reduced threads
            audio_codec='aac',
            verbose=True,
            logger='bar'
        )
        
        print("✅ Video created successfully!")
        
        # Close clips to free memory
        final_clip.close()
        bg_clip.close()
        for clip in valid_clips:
            if hasattr(clip, 'close'):
                clip.close()
        
    except Exception as e:
        print(f"❌ Video creation failed: {e}")
        print("Attempting simpler video creation...")
        
        # try:
        #     # Simpler approach - just video without complex audio mixing
        #     simple_clips = [bg_clip] + [clip for clip in text_clips if clip is not None]
        #     simple_video = CompositeVideoClip(simple_clips)
            
        #     simple_video.write_videofile(
        #         "src/outputs/final_simple.mp4",
        #         fps=24,
        #         threads=1,
        #         verbose=True
        #     )
        #     print("✅ Simple video created successfully!")
        #     simple_video.close()
        # except Exception as e2:
        #     print(f"❌ Even simple video creation failed: {e2}")

    # Delete src/imgs
    print("Cleaning up temporary files...")
    try:
        for img_file in os.listdir("src/imgs"):
            img_path = os.path.join("src/imgs", img_file)
            if os.path.isfile(img_path):
                os.remove(img_path)
        print("Deleted all imgs.")
    except Exception as e:
        print(f"Cleanup error: {e}")

    # Save used questions
    try:
        used_questions.update(selected_questions)
        with open("src/used_questions.json", "w") as f:
            json.dump(list(used_questions), f)
        print("Used questions updated.")
    except Exception as e:
        print(f"Error saving used questions: {e}")

    print("\n🎉 Process completed!")
    print(f"Check 'src/outputs/' for your video files.")


if __name__ == "__main__":
    create()