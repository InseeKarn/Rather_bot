# Dev by InseeKarn

from edit.edit import create
from youtube.upload import run_upload
from notify.discord import discord_message
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    create()  # create video
    video_url = run_upload()  # upload video
    if video_url:
        print("upload step pass")
        user_id = "304548816907010050"
        discord_message(f"✅ <@{user_id}> Uploaded vids: {video_url} ✅")  # notify discord
    else:
        print("⚠️ Upload failed, skipping Discord notify")
