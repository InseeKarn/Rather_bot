from flask import Flask, request, redirect, jsonify
import requests

app = Flask(__name__)

CLIENT_KEY = "sbawstaa06vtyabqgi"
CLIENT_SECRET = "fKeFdYATz6Okyuvjv0aSipGE8RNyt5Rx"
REDIRECT_URI = "http://localhost:5000/callback"  # ใช้ local server สำหรับ dev

@app.route("/")
def home():
    # ลิงก์ OAuth สำหรับผู้ใช้คลิก
    oauth_url = (
        "https://www.tiktok.com/auth/authorize?"
        f"client_key={CLIENT_KEY}&"
        "response_type=code&"
        "scope=user.info.basic,video.upload&"
        f"redirect_uri={REDIRECT_URI}&"
        "state=12345"
    )
    return f'<a href="{oauth_url}">Login with TikTok</a>'

@app.route("/callback")
def callback():
    # ดัก code และ state จาก TikTok
    code = request.args.get("code")
    state = request.args.get("state")

    if state != "12345":
        return "State mismatch!", 400

    # แลก code เป็น access token
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(url, data=data).json()

    return jsonify(response)  # แสดง access token + open_id

if __name__ == "__main__":
    app.run(debug=True)
