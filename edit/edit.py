import os
import json
import random
import shutil
import platform
from gtts import gTTS
from moviepy.editor import *
import moviepy.config as mpc

if platform.system() == "Windows":
    mpc.change_settings({
        "IMAGEMAGICK_BINARY": r"E:\\ImageMagick-7.1.2-Q16-HDRI\\magick.exe"
    })

os.makedirs("src/tts", exist_ok=True)

my_font = r"src/fonts/bold_font.ttf"

with open('would_you_rather.json', 'r') as f:
    data = json.load(f)

questions = data['questions']
selected_questions = random.sample(questions, 7)
backgrounds = ['src/template.png']

# Music
music_path = f"src/song/song.mp3"
music = AudioFileClip(music_path).volumex(0.2)

clips = []
text_clips = []
total_duration = 0
audio_clips = []

for i, q in enumerate(selected_questions):
    if ' or ' in q:
        option1, option2 = q.split(' or ', 1)
        option1, option2 = option1.strip(), option2.strip()
    else:
        option1, option2 = q, ""

    # TTS
    tts_file = f'src/tts/tts_{i}.mp3'
    tts = gTTS(text=q, lang='en')
    tts.save(tts_file)
    audio_clip = AudioFileClip(tts_file)


    txt_main_dura = audio_clip.duration
    wait_before_percent = 3
    percent_duration = 1.5
    wait_after_percent = 0.2
    end_time = txt_main_dura + wait_before_percent + percent_duration + wait_after_percent

    audio_clips.append(audio_clip.set_start(total_duration))

    # FX sound
    fx_clip = AudioFileClip("src/sfx/clock-ticking.mp3").set_start(total_duration + txt_main_dura).set_duration(wait_before_percent).volumex(0.5)
    audio_clips.append(fx_clip)

    num_ran = random.uniform(0.0, 100)

    # Text
    txt_top = TextClip(
        f"{option1}",
        fontsize=50, 
        color='white',
        font=my_font,
        method='caption',
        size=(700,100), 
        align='center'
    ).set_position(('center',50)).set_start(total_duration).set_duration(end_time)
    
    txt_bot = TextClip(
        f"{option2}",
        fontsize=50,
        color='white',
        font=my_font,
        method='caption',
        size=(700,300),
        align='center'
    ).set_position(('center',1050)).set_start(total_duration).set_duration(end_time)
    
    txt_or = TextClip(
        "OR",
        fontsize=70,
        color='yellow',
        font=my_font,
        method='caption',
        size=(700,100),
        align='center').set_position(('center',620)).set_start(total_duration).set_duration(end_time)
    
    txt_num1 = TextClip(
        f"{round(num_ran, 2)}%",
        fontsize=45,
        color="magenta",
        font=my_font,
        method="label",
            size=(300,100),
            align='center'
        ).set_position(('center',500)).set_start(total_duration + txt_main_dura + wait_before_percent).set_duration(percent_duration)
    
    txt_num2 = TextClip(
        f"{round(100.0 - round(num_ran, 2), 2)}%",
        fontsize=45,
        color="magenta",
        font=my_font,
        method="label",
        size=(300,100),
        align='center').set_position(('center',700)
    ).set_start(total_duration + txt_main_dura + wait_before_percent).set_duration(percent_duration)

    text_clips.extend([txt_top, txt_bot, txt_or, txt_num1, txt_num2])

    total_duration += end_time

# Background clip
bg_clip = ImageClip("src/template.png").resize((720,1280)).set_duration(total_duration)

# Composite
final_clip = CompositeVideoClip([bg_clip] + text_clips)

# Audio
final_audio = CompositeAudioClip(audio_clips + [music])
final_clip = final_clip.set_audio(final_audio)

final_clip.write_videofile("src/outputs/final.mp4", fps=24)

