# import os
# import json
# import random
# import platform
# import moviepy.config as mpc
# import pyttsx3


# from moviepy.editor import *


# if platform.system() == "Windows":
#     mpc.change_settings({
#         "IMAGEMAGICK_BINARY": r"E:\\ImageMagick-7.1.2-Q16-HDRI\\magick.exe"
#     })

# os.makedirs("src/tts", exist_ok=True)


# my_font = r"src/fonts/bold_font.ttf"

# with open('would_you_rather.json', 'r') as f:
#     data = json.load(f)
# questions = data['questions']


# # Load used_quest
# if os.path.exists("src/used_questions.json"):
#     with open("src/used_questions.json", "r") as f:
#         used_questions = set(json.load(f))
# else:
#     used_questions = []

# n = 5

# available = [q for q in questions if q not in used_questions]
# if len(available) < n:
#     # ลบคำถามที่เคยใช้ทั้งหมด
#     used_questions = []
#     available = questions.copy()

# selected_questions = random.sample(available, n)

# backgrounds = ['src/template.png']

# # Music
# music_path = f"src/song/song.mp3"
# music = AudioFileClip(music_path).volumex(0.2)

# clips = []
# text_clips = []
# total_duration = 0
# audio_clips = []

# # =============== Search IMG ========================

# import re
# import requests
# import numpy as np 
# from dotenv import load_dotenv
# from PIL import Image
# load_dotenv()

# API_KEY = os.getenv("GOOGLE_API")
# SEARCH_ID = os.getenv("GOOGLE_SEARCH_ID")

# os.makedirs("src/imgs", exist_ok=True)

# def search_image(query):
#     url = "https://www.googleapis.com/customsearch/v1"
#     params = {
#         "key": API_KEY,
#         "cx": SEARCH_ID,
#         "searchType": "image",
#         "q": query,
#         "num": 1,
#     }
#     resp = requests.get(url, params=params)
#     # print(resp.json())
#     data = resp.json()
#     if "items" in data and len(data["items"]) > 0:
#         return data["items"][0]["link"]
#     return None

# def download_image(url, save_path):
#     if not url:
#         return None
#     try:
#         r = requests.get(url, stream=True, timeout=5)
#         r.raise_for_status()  # Check status code
#         with open(save_path, "wb") as f:
#             for chunk in r.iter_content(1024):
#                 f.write(chunk)

#         try:
#             img = Image.open(save_path)
#             img.verify()
#             return save_path
#         except Exception as e:
#             print(f"File image damages: {save_path} | remove and skip: {e}")
#             os.remove(save_path)
#             return None
#     except requests.exceptions.RequestException as e:
#         print(f"Cannot download file from {url}: {e}")
#         return None
    
# def get_keywords(text, max_words=5):
#     text = re.sub(r'[^\w\s]', '', text)
#     words = text.split()
#     # Adjsut
#     keywords = [w for w in words if len(w) > 2]
#     return ' '.join(keywords[:max_words])

# def search_with_fallback(option):
#     query = get_keywords(option)
#     print("Trying keyword search:", query)  # <-- debug
#     url = search_image(query)
#     if url:
#         return url
    
#     return search_progressive(option)

# def search_progressive(option):
#     words = option.split()
#     n = 1
#     while n <= len(words):
#         # สร้างทุก combination ของ n คำต่อเนื่อง
#         found = False
#         for start in range(len(words) - n + 1):
#             query = ' '.join(words[start:start+n])
#             url = search_image(query)
#             if url:
#                 return url  # เจอแล้ว return ทันที
#         n += 1  # เพิ่มจำนวนคำต่อ search
#     return None  # ไม่เจอเลย

# def safe_imageclip(path, pos, start, duration, resize=0.5):
#     if not path or not os.path.exists(path):
#         return None
#     try:
#         img = Image.open(path).convert("RGB")
#         img.thumbnail((720, 1280), Image.ANTIALIAS)  # ลดขนาด
#         clip = ImageClip(np.array(img)).resize(resize).set_position(pos).set_start(start).set_duration(duration)
#         return clip
#     except Exception as e:
#         print(f"Cannot load image {path}: {e}")
#         return None
    
# top_img_paths = []
# bot_img_paths = []

# for i, q in enumerate(selected_questions):
#     try:
#         if ' or ' in q:
#             option1, option2 = q.split(' or ', 1)
#         else:
#             option1, option2 = q, ""

#         # Top image
#         top_img_path = f"src/imgs/top_image_{i}.jpg"
#         url = search_with_fallback(option1)
#         top_img_path = download_image(url, top_img_path)
#         if top_img_path:
#             print(f"Top image {i} downloaded: {top_img_path}")
#         else:
#             print(f"Top image {i} failed, skipped")
#             top_img_path = None
#         top_img_paths.append(top_img_path)

#         # Bot image
#         bot_img_path = f"src/imgs/bot_image_{i}.jpg"
#         url = search_with_fallback(option2)
#         bot_img_path = download_image(url, bot_img_path)
#         if bot_img_path:
#             print(f"Bot image {i} downloaded: {bot_img_path}")
#         else:
#             print(f"Bot image {i} failed, skipped")
#             bot_img_path = None
#         bot_img_paths.append(bot_img_path)

#     except Exception as e:
#         print(f"Image download error at question {i}: {e}")
#         top_img_paths.append(None)
#         bot_img_paths.append(None)

# def safe_imageclip(path, pos, start, duration, resize=0.5):
#     if not path or not os.path.exists(path):
#         return None
#     try:
#         img = Image.open(path).convert("RGB")
#         img = img.resize((int(img.width*resize), int(img.height*resize)))
#         return ImageClip(np.array(img)).set_position(pos).set_start(start).set_duration(duration)
#     except Exception as e:
#         print(f"Cannot load image {path}: {e}")
#         return None


# # =============== Search IMG ========================

# for i, q in enumerate(selected_questions):
#     if ' or ' in q:
#         option1, option2 = q.split(' or ', 1)
#         option1, option2 = option1.strip(), option2.strip()
#     else:
#         option1, option2 = q, ""

#     # TTS

#     engine = pyttsx3.init()
#     engine.setProperty('rate', 150)  # ความเร็วพูด
#     engine.setProperty('volume', 1.0)  # ระดับเสียง

#     tts_file = f'src/tts/tts_{i}.mp3'
#     engine.save_to_file(q, tts_file)
#     engine.runAndWait()

#     audio_clip = AudioFileClip(tts_file)


#     txt_main_dura = audio_clip.duration
#     wait_before_percent = 3
#     percent_duration = 1.5
#     wait_after_percent = 0.2
#     end_time = txt_main_dura + wait_before_percent + percent_duration + wait_after_percent

#     audio_clips.append(audio_clip.set_start(total_duration))

#     # FX sound
#     fx_clip = AudioFileClip("src/sfx/clock-ticking.mp3").set_start(total_duration + txt_main_dura).set_duration(wait_before_percent).volumex(0.5)
#     audio_clips.append(fx_clip)

#     num_ran = random.uniform(0.0, 100)

#     # Text
#     txt_top = TextClip(
#         f"{option1}",
#         fontsize=50, 
#         color='white',
#         font=my_font,
#         method='caption',
#         size=(700,100), 
#         align='center'
#     ).set_position(('center',50)).set_start(total_duration).set_duration(end_time)
    
#     txt_bot = TextClip(
#         f"{option2}",
#         fontsize=50,
#         color='white',
#         font=my_font,
#         method='caption',
#         size=(700,300),
#         align='center'
#     ).set_position(('center',1050)).set_start(total_duration).set_duration(end_time)
    
#     txt_or = TextClip(
#         "OR",
#         fontsize=70,
#         color='yellow',
#         font=my_font,
#         method='label',
#         size=(700,100),
#         align='center').set_position(('center',620)).set_start(total_duration).set_duration(end_time)
    
#     txt_num1 = TextClip(
#         f"{round(num_ran, 2)}%",
#         fontsize=45,
#         color="magenta",
#         font=my_font,
#         method="label",
#             size=(300,100),
#             align='center'
#         ).set_position(('center',500)).set_start(total_duration + txt_main_dura + wait_before_percent).set_duration(percent_duration)
    
#     txt_num2 = TextClip(
#         f"{round(100.0 - round(num_ran, 2), 2)}%",
#         fontsize=45,
#         color="magenta",
#         font=my_font,
#         method="label",
#         size=(300,100),
#         align='center').set_position(('center',720)
#     ).set_start(total_duration).set_duration(end_time)
    
#     # --- Debug TextClip ---
#     for name, clip in [("txt_top", txt_top), ("txt_bot", txt_bot), ("txt_or", txt_or), ("txt_num1", txt_num1), ("txt_num2", txt_num2)]:
#         if clip is None:
#             print(f"[DEBUG] {name} is None for question {i}")
#         else:
#             print(f"[DEBUG] {name} created: duration={clip.duration}, position={clip.pos}")
    
#     # --- Top Image ---
#     top_clip = safe_imageclip(top_img_paths[i], ("center",450), total_duration, end_time)
#     if top_clip is None:
#         top_clip = ColorClip(size=(720,300), color=(0,0,0)).set_start(total_duration).set_duration(end_time)

#     # --- Bot Image ---
#     bot_clip = safe_imageclip(bot_img_paths[i], ("center",770), total_duration, end_time)
#     if bot_clip is None:
#         bot_clip = ColorClip(size=(720,300), color=(0,0,0)).set_start(total_duration).set_duration(end_time)

#     # --- Debug ImageClip ---
#     for name, path, clip in [("top_clip", top_img_paths[i], top_clip), ("bot_clip", bot_img_paths[i], bot_clip)]:
#         if clip is None:
#             print(f"[DEBUG] {name} is None! path={path}")
#         else:
#             print(f"[DEBUG] {name} created: duration={clip.duration}, size={clip.size}, position={clip.pos}")

#     # Add clips if not None
#     clips.extend([c for c in [top_clip, bot_clip] if c])

    
#     text_clips.extend([txt_top, txt_bot, txt_or, txt_num1, txt_num2])

#     total_duration += end_time

# # Background clip
# bg_clip = ImageClip("src/template.png").resize((720,1280)).set_duration(total_duration)


# try:
#     final_clip = CompositeVideoClip([bg_clip] + text_clips + clips)
#     final_audio = CompositeAudioClip(audio_clips + [music])
#     final_clip = final_clip.set_audio(final_audio)
#     final_clip.write_videofile(
#         "src/outputs/final.mp4",
#         fps=24,
#         threads=4,
#         logger=None
#         )
# except Exception as e:
#     print(f"Video creation failed: {e}")

# # Delete src/imgs
# for img_file in os.listdir("src/imgs"):
#     img_path = os.path.join("src/imgs", img_file)
#     if os.path.isfile(img_path):
#         os.remove(img_path)
# print("Deleted all imgs.")

# # Save used quest
# with open("src/used_questions.json", "w") as f:
#     json.dump(list(used_questions), f)

import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 720, 1280
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Debug Mouse Position")

WHITE = (255, 255, 255)
RED = (255, 0, 0)

x, y = WIDTH // 2, HEIGHT // 2
radius = 50

font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

while True:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # วาดวงกลม
    pygame.draw.circle(screen, RED, (x, y), radius)
    
    # ตำแหน่งเมาส์
    mouse_pos = pygame.mouse.get_pos()
    
    # แสดงตำแหน่งเมาส์บนหน้าจอ
    pos_text = font.render(f"Mouse: {mouse_pos}", True, (0, 0, 0))
    screen.blit(pos_text, (20, 20))
    
    # พิมพ์ตำแหน่งเมาส์บนคอนโซล
    print(mouse_pos)
    
    pygame.display.flip()
    clock.tick(60)

