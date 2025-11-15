"""
Script to generate valid token.json for YouTube API
Run this locally to create the token, then copy it to GitHub Secrets
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import json

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def generate_token():
    """Generate token.json from credentials.json"""
    
    print("🔐 Starting OAuth flow...")
    print("📌 Make sure you have credentials.json in the same directory!")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", 
            SCOPES
        )
        
        # This will open browser for authorization
        creds = flow.run_local_server(
            port=0,
            access_type="offline",
            prompt="consent"  # Force to get refresh_token
        )
        
        # Save token
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        
        print("✅ Token generated successfully!")
        print("📄 File saved as: token.json")
        
        # Display token content (for copying to GitHub Secrets)
        with open("token.json", "r") as f:
            token_data = json.load(f)
        
        print("\n" + "="*60)
        print("📋 Copy this to GitHub Secrets as TOKEN_JSON:")
        print("="*60)
        print(json.dumps(token_data, indent=2))
        print("="*60)
        
        # Verify token structure
        required_fields = ["client_id", "client_secret", "refresh_token"]
        missing = [f for f in required_fields if f not in token_data]
        
        if missing:
            print(f"\n⚠️ WARNING: Missing fields: {missing}")
            print("This token might not work properly!")
        else:
            print("\n✅ Token structure is valid!")
            
    except FileNotFoundError:
        print("❌ Error: credentials.json not found!")
        print("📌 Download it from: https://console.cloud.google.com/apis/credentials")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_token()