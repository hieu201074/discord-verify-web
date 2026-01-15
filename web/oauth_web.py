from flask import Flask, request
import requests, os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")

API = "https://discord.com/api/v10"

@app.route("/")
def verify():
    uid = request.args.get("uid")
    if not uid:
        return "Thiếu user ID"

    headers = {"Authorization": f"Bot {BOT_TOKEN}"}

    user = requests.get(f"{API}/users/{uid}", headers=headers).json()
    if "id" not in user:
        return "Không tìm thấy user"

    avatar_url = f"https://cdn.discordapp.com/avatars/{uid}/{user['avatar']}.png?size=256"

    member = requests.get(
        f"{API}/guilds/{GUILD_ID}/members/{uid}",
        headers=headers
    ).json()

    if VERIFY_ROLE_ID not in member.get("roles", []):
        requests.put(
            f"{API}/guilds/{GUILD_ID}/members/{uid}/roles/{VERIFY_ROLE_ID}",
            headers=headers
        )

    html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Verify Success</title>
<style>
body {{
    margin:0;
    height:100vh;
    background:linear-gradient(135deg,#1e3c72,#2a5298);
    display:flex;
    justify-content:center;
    align-items:center;
    font-family:Segoe UI;
    color:white;
}}
.card {{
    background:rgba(255,255,255,.12);
    backdrop-filter:blur(15px);
    padding:45px 55px;
    border-radius:24px;
    text-align:center;
    box-shadow:0 20px 45px rgba(0,0,0,.45);
    animation:fade .8s ease;
}}
.card img {{
    width:120px;
    height:120px;
    border-radius:50%;
    border:4px solid #fff;
    margin-bottom:15px;
}}
.badge {{
    margin-top:18px;
    padding:12px 25px;
    border-radius:30px;
    background:#4CAF50;
    font-weight:700;
    font-size:18px;
}}

/* DEV CARD */
.dev {{
    position:fixed;
    top:18px;
    right:18px;
    background:rgba(0,0,0,.45);
    padding:12px 18px;
    border-radius:18px;
    display:flex;
    align-items:center;
    gap:10px;
    backdrop-filter:blur(10px);
    cursor:pointer;
    transition:.3s;
}}
.dev:hover {{
    transform:translateY(-4px) scale(1.05);
    box-shadow:0 12px 25px rgba(0,0,0,.5);
}}
.dev img {{
    width:28px;
    height:28px;
}}
.dev span {{
    font-size:14px;
    white-space:nowrap;
}}
.fb {{
    margin-left:8px;
    background:#1877f2;
    color:white;
    padding:4px 10px;
    border-radius:10px;
    font-size:12px;
    text-decoration:none;
    transition:.3s;
}}
.fb:hover {{
    background:#0f5bd8;
}}

@keyframes fade {{
    from {{opacity:0; transform:translateY(15px)}}
    to {{opacity:1; transform:none}}
}}
</style>
</head>
<body>

<!-- DEV CARD -->
<div class="dev">
    <img src="https://cdn-icons-png.flaticon.com/512/2111/2111370.png">
    <span>Dev Code By <b>Minh Hieu</b></span>
    <a class="fb" href="https://facebook.com/banlagiv" target="_blank">FB</a>
</div>

<div class="card">
    <img src="{avatar_url}">
    <h1>{user['username']}#{user['discriminator']}</h1>
    <div class="badge">ĐÃ XÁC MINH</div>
</div>

</body>
</html>
"""
    return html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)