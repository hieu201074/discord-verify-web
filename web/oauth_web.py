import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# ========= ENV =========
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "❌ Thiếu code OAuth"

    # ===== ĐỔI CODE -> ACCESS TOKEN =====
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
        return f"❌ OAuth2 thất bại: {token_res}"

    # ===== LẤY USER =====
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

    # ===== HTML =====
    html = """
<!DOCTYPE html>
<html lang="vi">
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

/* CARD GIỮA */
.card{
    background:linear-gradient(135deg,#5865F2,#8b5cf6);
    padding:45px;
    border-radius:25px;
    text-align:center;
    box-shadow:0 25px 60px rgba(0,0,0,.6);
}
.avatar{
    width:120px;
    height:120px;
    border-radius:50%;
    border:4px solid white;
    margin-bottom:15px;
}
.verified{
    margin-top:10px;
    font-size:14px;
    opacity:.95;
}

/* CARD DEV */
.dev-card{
    position:fixed;
    top:20px;
    right:20px;
    background:#111827;
    padding:15px 18px;
    border-radius:18px;
    box-shadow:0 15px 40px rgba(0,0,0,.7);
    transition:.3s;
}
.dev-card:hover{
    transform:translateY(-6px);
}

/* DEV HEADER + BADGE */
.dev-header{
    display:flex;
    align-items:center;
    gap:8px;
    margin-bottom:8px;
}
.dev-badge{
    width:22px;
    height:22px;
    border-radius:50%;
    background:linear-gradient(135deg,#5865F2,#22d3ee);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:12px;
    box-shadow:0 0 12px rgba(88,101,242,.9);
    transition:.3s;
}
.dev-card:hover .dev-badge{
    transform:rotate(20deg) scale(1.15);
}

.dev-name{
    font-size:14px;
    font-weight:600;
}

/* FB BUTTON */
.fb-btn{
    display:inline-block;
    padding:6px 14px;
    background:#1877F2;
    border-radius:12px;
    font-size:12px;
    color:white;
    text-decoration:none;
    transition:.25s;
}
.fb-btn:hover{
    background:#0f5ecb;
}
</style>
</head>
<body>

<!-- CARD GIỮA -->
<div class="card">
    <img class="avatar" src="{{avatar}}">
    <h2>{{username}}</h2>
    <div class="verified">✔ Verified</div>
</div>

<!-- CARD DEV -->
<div class="dev-card">
    <div class="dev-header">
        <div class="dev-badge">★</div>
        <div class="dev-name">Dev Code By Minh Hieu</div>
    </div>
    <a class="fb-btn" href="https://facebook.com/banlagiv" target="_blank">Facebook</a>
</div>

</body>
</html>
"""
    return render_template_string(
        html,
        username=user["username"],
        avatar=avatar
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)