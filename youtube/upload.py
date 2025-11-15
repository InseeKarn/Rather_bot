import os
import random
from dotenv import load_dotenv

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import json

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
load_dotenv()
youtube_api = os.getenv("GOOGLE_API")


def get_service():
    """
    created and return service object YouTube API
    """
    creds = None  # token/credentials

    # Check if token.json exists and is valid
    if os.path.exists("token.json"):
        try:
            # Try to load and validate token structure
            with open("token.json", "r") as f:
                token_data = json.load(f)
            
            # Check for required fields
            required_fields = ["client_id", "client_secret", "refresh_token"]
            missing = [f for f in required_fields if f not in token_data]
            
            if missing:
                print(f"⚠️ token.json is missing fields: {missing}")
                print("⚠️ Token is invalid. Need to regenerate.")
                raise ValueError("Invalid token.json structure")
            
            # Load credentials
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
            print("✅ Token loaded successfully")
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️ token.json is invalid: {e}")
            creds = None

    # if not or token expire → create new OAuth flow 
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully")
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                raise
        else:
            # This won't work in GitHub Actions without manual authorization
            print("❌ No valid credentials found!")
            print("📌 You need to generate token.json locally first")
            print("📌 Run: python generate_token.py")
            raise RuntimeError(
                "No valid token.json found. "
                "Please generate it locally and add to GitHub Secrets."
            )
            
        # Save refreshed token
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        print("💾 Updated token.json saved")

    # build YouTube API service object
    return build("youtube", "v3", credentials=creds)

def upload_video(file_path, title, description, 
                 category=None, privacy=None):
    """
    Upload YouTube videos
    """
    youtube = get_service()  # get service object

    # load .env if not have use , ""
    category = category or os.getenv("YT_CATEGORY", "24")
    privacy = privacy or os.getenv("YT_PRIVACY", "unlisted")

    #body (data of videos)
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category,
            "tags": [
                "shorts", "fyp", "viral", "wouldyourather", "thisorthat",
                "funchoices", "wouldyouratherchallenge", "choicegame",
            ]
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        }
    }

    # Prepare file to upload
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    # request to API
    request = youtube.videos().insert(
        part="snippet,status",  # Must match fields in body
        body=body,
        media_body=media
    )

    print(f"📤 Uploading video...")
    response = request.execute()  # wait for result
    video_id = response["id"]     # save videoId 
    video_url = f"https://youtu.be/{video_id}"
    print(f"✅ Uploaded: {video_url}")
    return video_url
    
def run_upload():
    title_ran = random.choice([
        "99% Can't Decide This! 😱",
        "Only Brave People Can Choose… Dare You? 🤯",
        "This Choice Will Break Your Brain! 🧠💥",
        "WARNING: Once You Choose, You Can't Undo! ⚠️",
        "The HARDEST Would You Rather EVER! 😳",
        ])

    clean_title = " ".join(title_ran.split())
    # x <= 100
    clean_title = clean_title[:100]

    description_ran = random.choice([
        "🧠 Test your choices with fun Would You Rather questions! #shorts #fyp",
        "🤔 Can you make the tough choice? Try now! #shorts #fyp",
        "🎯 Challenge your friends and see their decisions! #shorts #fyp",
        "⚡ Interactive Would You Rather game for everyone! #shorts #fyp",
        "⏱️ Think fast and make the right choice! #shorts #fyp"
    ])

    file_path = "src/outputs/final.mp4"
    
    try:
        video_url = upload_video(
            file_path=file_path,
            title=clean_title,
            description=description_ran
        )
        
        # 🆕 Delete after uploaded
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️ Deleted file: {file_path}")
            except Exception as e:
                print(f"⚠️ Failed to delete file: {e}")

        return video_url
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print("\n💡 Common solutions:")
        print("1. Generate token.json locally: python generate_token.py")
        print("2. Copy token.json content to GitHub Secret: TOKEN_JSON")
        print("3. Make sure credentials.json is valid")
        return None

if __name__ == "__main__":
    run_upload()