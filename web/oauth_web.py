from flask import Flask, request, render_template_string
import requests, os

app = Flask(__name__)

# ========================
# ENV Variables
# ========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GUILD_ID = os.getenv("GUILD_ID")
VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")
REDIRECT_URL = os.getenv("REDIRECT_URL")
GIF_URL = os.getenv("GIF_URL", "https://cdn.discordapp.com/attachments/1200665203004674088/1460716084213846188/93384E15-2EB0-43E1-94AE-D470EC7E3119.gif")

# ========================
# Route test server
# ========================
@app.route("/")
def index():
    return "✅ Server chạy OK! Nhấn verify trên Discord để tới /callback"

# ========================
# Route verify Discord
# ========================
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "❌ Lỗi xác minh: không có code từ Discord OAuth2"

    # Lấy token OAuth2
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
        return "❌ OAuth2 thất bại: {token_res}"

    # Lấy thông tin user
    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    avatar_url = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png?size=256"

    # Cấp role verify
    r = requests.put(
        f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user['id']}/roles/{VERIFY_ROLE_ID}",
        headers={"Authorization": f"Bot {BOT_TOKEN}"}
    )
    if r.status_code not in (200, 204):
        return "❌ Không cấp được role"

    # HTML verify full (button nhẹ nhàng + emoji animation + confetti)
    html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>✅ Xác minh thành công</title>
<style>
body {{
    margin:0; padding:0; height:100vh;
    display:flex; justify-content:center; align-items:center;
    font-family:'Segoe UI', Tahoma, sans-serif;
    overflow:hidden;
    background: url('{GIF_URL}') center/cover no-repeat;
}}
.card {{
    background: rgba(0,0,0,0.5);
    padding: 50px 60px;
    border-radius:20px;
    text-align:center;
    color:white;
    box-shadow:0 8px 30px rgba(0,0,0,0.5);
    animation: fadeIn 1s ease forwards;
    display:flex; flex-direction:column; align-items:center; gap:20px;
}}
h1 {{ font-size:3em; margin:0; animation:bounce 1s; }}
p {{ font-size:1.5em; margin:0; }}
.avatar {{
    width:128px; height:128px; border-radius:50%;
    border:4px solid #ffce00;
    box-shadow:0 4px 15px rgba(0,0,0,0.5);
    animation:fadeIn 2s ease forwards;
}}
a.button {{
    text-decoration:none;
    background: rgba(114,137,218,0.85);
    color: white;
    padding: 0.8em 1.5em;
    border-radius: 12px;
    font-weight: 500;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    transition: 0.25s all ease-in-out;
    display:inline-flex; align-items:center; gap:8px;
}}
a.button:hover {{
    background: rgba(114,137,218,1);
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}}
span.emoji {{
    display:inline-block;
    transition: transform 0.3s ease;
}}
a.button:active span.emoji {{
    transform: scale(1.3) rotate(15deg);
}}
/* Animations */
@keyframes fadeIn {{ 0%{{opacity:0; transform:translateY(-20px);}} 100%{{opacity:1; transform:translateY(0);}} }}
@keyframes bounce {{ 0%,20%,50%,80%,100%{{transform:translateY(0);}} 40%{{transform:translateY(-15px);}} 60%{{transform:translateY(-8px);}} }}
.confetti {{ position: fixed; width: 10px; height: 10px; background: yellow; animation: confettiFall 3s linear infinite; }}
@keyframes confettiFall {{ 0%{{transform:translateY(0) rotate(0deg);}} 100%{{transform:translateY(100vh) rotate(360deg);}} }}
</style>
</head>
<body>
<div class="card">
    <img class="avatar" src="{avatar_url}" alt="Avatar Discord">
    <h1>✅ Xác minh thành công!</h1>
    <p>Xin chào <b>{user['username']}</b></p>
    <a class="button" href="https://discord.com/app">
        <span class="emoji">💖</span> Quay lại Discord
    </a>
</div>

<script>
function createConfetti(){{
    for(let i=0;i<30;i++){{
        const conf=document.createElement('div');
        conf.className='confetti';
        conf.style.left=Math.random()*100+'vw';
        conf.style.background=`hsl(${Math.random()*360},100%,50%)`;
        conf.style.animationDuration=(Math.random()*2+2)+'s';
        conf.style.width=conf.style.height=(Math.random()*8+4)+'px';
        document.body.appendChild(conf);
        setTimeout(()=>conf.remove(),3000);
    }}
}}
createConfetti();
</script>
</body>
</html>
"""
    return html

# ========================
# Run Flask server Render
# ========================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)