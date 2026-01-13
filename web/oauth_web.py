# oauth_web_gradient.py
from flask import Flask, request, render_template_string
import requests, urllib.parse, os

app = Flask(__name__)

# -----------------------------
# CẤU HÌNH
# -----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GUILD_ID = os.getenv("GUILD_ID")
VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")
REDIRECT_URL = os.getenv("REDIRECT_URL")  # https://discord-verify-web.onrender.com/callback

# Tạo Verify URL
encoded_redirect = urllib.parse.quote(REDIRECT_URL, safe='')
VERIFY_URL = f"https://discord.com/api/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={encoded_redirect}&response_type=code&scope=identify%20guilds.join"

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def index():
    return f'''
    <div style="display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;">
        <a href="{VERIFY_URL}" style="text-decoration:none;font-size:22px;background:#7289da;color:white;padding:20px 40px;border-radius:20px;box-shadow:0 4px 15px rgba(0,0,0,0.3);">
            ➡️ Nhấn để Verify Discord
        </a>
    </div>
    '''

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "❌ Không có code OAuth2"

    # --- Lấy access token ---
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URL
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    token_res = requests.post(
        "https://discord.com/api/oauth2/token",
        data=urllib.parse.urlencode(data),
        headers=headers
    ).json()

    if "access_token" not in token_res:
        return f"❌ OAuth2 thất bại: {token_res}"

    access_token = token_res["access_token"]

    # --- Lấy info user ---
    user_res = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    if "id" not in user_res:
        return f"❌ Lấy user thất bại: {user_res}"

    user_id = user_res["id"]
    username = user_res.get("username", "Unknown")
    avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{user_res.get('avatar','')}.png?size=256"

    # --- Gán role verify ---
    r = requests.put(
        f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user_id}/roles/{VERIFY_ROLE_ID}",
        headers={"Authorization": f"Bot {BOT_TOKEN}"}
    )
    if r.status_code not in (200, 204):
        return f"❌ Không cấp được role: {r.text}"

    # --- Page verify gradient card & button ---
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
    font-family: 'Segoe UI', Tahoma, sans-serif;
    background:#121212;
    color:white;
    overflow:hidden;
}}
.card {{
    background: linear-gradient(145deg, #4e54c8, #8f94fb);
    padding:50px 60px;
    border-radius:25px;
    text-align:center;
    box-shadow:0 10px 40px rgba(0,0,0,0.6);
    display:flex;
    flex-direction:column;
    align-items:center;
    gap:25px;
    animation:fadeIn 1s ease forwards;
}}
h1{{ font-size:3em; margin:0; animation:bounce 1s; }}
p{{ font-size:1.5em; margin:0; }}
.avatar{{ width:128px; height:128px; border-radius:50%; border:4px solid #ffce00; box-shadow:0 4px 20px rgba(0,0,0,0.6); }}
a.button{{
    text-decoration:none;
    background: linear-gradient(45deg, #ff6ec4, #7873f5);
    color:white;
    padding:1em 2.5em;
    border-radius:25px;
    font-weight:bold;
    box-shadow:0 5px 20px rgba(0,0,0,0.4);
    transition:0.3s transform,0.3s box-shadow;
    display:inline-flex;
    align-items:center;
    gap:12px;
    font-size:1.3em;
}}
a.button:hover{{ transform:translateY(-4px) scale(1.05); box-shadow:0 10px 25px rgba(0,0,0,0.6); }}
.emoji{{ animation:wiggle 1s infinite; }}
.confetti {{
    position: fixed; width:10px; height:10px; background: yellow;
    animation: confettiFall 3s linear infinite;
}}
@keyframes fadeIn{{0%{{opacity:0; transform:translateY(-20px);}}100%{{opacity:1; transform:translateY(0);}}}}
@keyframes bounce{{0%,20%,50%,80%,100%{{transform:translateY(0);}}40%{{transform:translateY(-15px);}}60%{{transform:translateY(-8px);}}}}
@keyframes wiggle{{0%,100%{{transform:rotate(0deg);}}25%{{transform:rotate(15deg);}}50%{{transform:rotate(-10deg);}}75%{{transform:rotate(10deg);}}}}
@keyframes confettiFall{{0%{{transform:translateY(0) rotate(0deg);}}100%{{transform:translateY(100vh) rotate(360deg);}}}}
</style>
</head>
<body>
<div class="card">
    <img class="avatar" src="{avatar_url}" alt="Avatar Discord">
    <h1>✅ Xác minh thành công!</h1>
    <p>Xin chào <b>{username}</b></p>
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
    return render_template_string(html)

# -----------------------------
# RUN FLASK
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)