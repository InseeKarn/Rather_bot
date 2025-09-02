import os
import json
import random
from gtts import gTTS
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
from moviepy.config import change_settings

change_settings({"IMAGEMAGICK_BINARY": r"E:/ImageMagick-7.1.2-Q16-HDRI/magick.exe"})

os.makedirs("src/tts", exist_ok=True)

my_font = r"src/fonts/bold_font.ttf"

with open('would_you_rather.json', 'r') as f:
    data = json.load(f)

questions = data['questions']
selected_questions = random.sample(questions, 12)
backgrounds = ['src/template.png']

clips = []

for i, q in enumerate(selected_questions):
    if ' or ' in q:
        option1, option2 = q.split(' or ', 1)
    else:
        option1, option2 = q, ""

    bg_clip = ImageClip(random.choice(backgrounds)).set_duration(5).resize((720,1280))

    # TTS
    tts_file = f'src/tts/tts_{i}.mp3'
    tts = gTTS(text=q, lang='en')
    tts.save(tts_file)
    audio_clip = AudioFileClip(tts_file)

    txt_top = TextClip(
        "OR",
        fontsize=70,
        color='yellow',
        font=my_font,
        method='caption',
        size=(700, 100),
        align='center'
    ).set_position(('center', 50)).set_duration(5)

    txt_bottom = TextClip(
        f"{option1}\nOR\n{option2}",
        fontsize=50,
        color='white',
        font=my_font,
        method='caption',
        size=(700, 300),
        align='center'
    ).set_position(('center', 900)).set_duration(5)

    clip = CompositeVideoClip([bg_clip, txt_top, txt_bottom]).set_audio(audio_clip)
    clips.append(clip)

final_clip = concatenate_videoclips(clips, method="compose")
final_clip.write_videofile("would_you_rather_video.mp4", fps=24)
