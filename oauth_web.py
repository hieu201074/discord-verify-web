import os
from flask import Flask, redirect, request
import requests

app = Flask(__name__)

# ===== LẤY BIẾN MÔI TRƯỜNG (ENV) =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GUILD_ID = os.getenv("GUILD_ID")
VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")
REDIRECT_URL = os.getenv("REDIRECT_URL")

PORT = int(os.environ.get("PORT", 10000))

# ===== LINK OAUTH2 =====
AUTH_URL = (
    "https://discord.com/api/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    "&response_type=code"
    "&scope=identify"
    f"&redirect_uri={REDIRECT_URL}"
)

@app.route("/")
def index():
    return redirect(AUTH_URL)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "❌ Lỗi xác minh"

    # Lấy access token
    token_res = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URL
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    ).json()

    access_token = token_res.get("access_token")
    if not access_token:
        return "❌ OAuth2 thất bại"

    # Lấy user info
    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    # Add role verify
    r = requests.put(
        f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user['id']}/roles/{VERIFY_ROLE_ID}",
        headers={"Authorization": f"Bot {BOT_TOKEN}"}
    )

    if r.status_code not in (200, 204):
        return "❌ Không cấp được role"

    return f"""
    <h1 style='color:green'>✅ XÁC MINH THÀNH CÔNG</h1>
    <p>Xin chào <b>{user['username']}</b></p>
    <a href="https://discord.com/app">Quay lại Discord</a>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)