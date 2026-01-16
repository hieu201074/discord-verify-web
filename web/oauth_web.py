import os
import requests
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

# ========= ENV =========
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")


# ========= HOME =========
@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>Verify</title>
<style>
body{
    margin:0;
    height:100vh;
    display:flex;
    justify-content:center;
    align-items:center;
    background:#0b0f1a;
    font-family:Segoe UI,sans-serif;
    color:white;
}
.box{
    background:#111827;
    padding:40px;
    border-radius:22px;
    text-align:center;
    box-shadow:0 20px 60px rgba(0,0,0,.6);
}
a{
    display:inline-block;
    margin-top:18px;
    padding:12px 26px;
    background:#5865F2;
    color:white;
    text-decoration:none;
    border-radius:14px;
    font-weight:600;
}
</style>
</head>
<body>
<div class="box">
    <h2>Verification</h2>
    <p>Nhấn nút dưới để xác minh</p>
    <a href="/login">Verify</a>
</div>
</body>
</html>
"""


# ========= LOGIN =========
@app.route("/login")
def login():
    return redirect(
        "https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=identify"
    )


# ========= CALLBACK =========
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "❌ Thiếu code OAuth"

    token_res = requests.post(
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    ).json()

    access_token = token_res.get("access_token")
    if not access_token:
        return f"❌ OAuth2 lỗi: {token_res}"

    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    avatar = (
        f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png?size=256"
        if user.get("avatar")
        else "https://cdn.discordapp.com/embed/avatars/0.png"
    )

    # ===== CẤP ROLE =====
    requests.put(
        f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user['id']}/roles/{VERIFY_ROLE_ID}",
        headers={"Authorization": f"Bot {BOT_TOKEN}"}
    )

    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Verified</title>
<style>
body{
    margin:0;
    height:100vh;
    background:#0b0f1a;
    display:flex;
    justify-content:center;
    align-items:center;
    font-family:Segoe UI,sans-serif;
    color:white;
}
.card{
    background:linear-gradient(135deg,#5865F2,#8b5cf6);
    padding:45px;
    border-radius:25px;
    text-align:center;
}
.avatar{
    width:120px;
    height:120px;
    border-radius:50%;
    border:4px solid white;
}
.dev-card{
    position:fixed;
    top:20px;
    right:20px;
    background:#111827;
    padding:15px;
    border-radius:18px;
}
.dev-badge{
    width:22px;
    height:22px;
    border-radius:50%;
    background:#5865F2;
    display:inline-flex;
    align-items:center;
    justify-content:center;
}
</style>
</head>
<body>

<div class="card">
    <img class="avatar" src="{{avatar}}">
    <h2>{{username}}</h2>
    <div>✔ Verified</div>
</div>

<div class="dev-card">
    <div class="dev-badge">★</div>
    Dev Code By Minh Hieu
</div>

</body>
</html>
"""
    return render_template_string(html, username=user["username"], avatar=avatar)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)