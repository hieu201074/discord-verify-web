import os, requests
from flask import Flask, request, redirect, render_template_string
from urllib.parse import quote

app = Flask(__name__)

# ===== ENV =====
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")

TURNSTILE_SITE_KEY = os.getenv("TURNSTILE_SITE_KEY")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY")

REDIRECT_URI_ENCODED = quote(REDIRECT_URI, safe="")

# ===== HOME =====
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        captcha = request.form.get("cf-turnstile-response")
        if not captcha:
            return "Captcha required"

        verify = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": TURNSTILE_SECRET_KEY,
                "response": captcha,
                "remoteip": request.remote_addr
            }
        ).json()

        if not verify.get("success"):
            return "Captcha failed"

        return redirect("/login")

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Verify</title>
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
<style>
body{
    margin:0;height:100vh;
    display:flex;justify-content:center;align-items:center;
    background:#0b0f1a;color:white;
    font-family:Segoe UI,sans-serif;
}
.box{
    background:#111827;
    padding:48px;border-radius:30px;
    text-align:center;
    box-shadow:0 25px 80px rgba(0,0,0,.7);
}
button{
    margin-top:20px;
    padding:14px 36px;
    border:none;border-radius:18px;
    background:#5865F2;
    color:white;font-weight:600;
    cursor:pointer;
}
</style>
</head>
<body>
<form method="POST" class="box">
<h2>Server Verification</h2>
<p>Xác minh để tiếp tục</p>
<div class="cf-turnstile" data-sitekey="{{sitekey}}"></div>
<button type="submit">Continue</button>
</form>
</body>
</html>
""", sitekey=TURNSTILE_SITE_KEY)

# ===== LOGIN =====
@app.route("/login")
def login():
    return redirect(
        "https://discord.com/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI_ENCODED}"
        "&response_type=code"
        "&scope=identify%20guilds.join"
    )

# ===== CALLBACK =====
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing OAuth code"

    token = requests.post(
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

    access_token = token.get("access_token")
    if not access_token:
        return "OAuth expired"

    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    user_id = user["id"]

    # Join guild
    requests.put(
        f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user_id}",
        headers={
            "Authorization": f"Bot {BOT_TOKEN}",
            "Content-Type": "application/json"
        },
        json={"access_token": access_token}
    )

    # Add role
    requests.put(
        f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user_id}/roles/{VERIFY_ROLE_ID}",
        headers={"Authorization": f"Bot {BOT_TOKEN}"}
    )

    avatar = (
        f"https://cdn.discordapp.com/avatars/{user_id}/{user['avatar']}.png?size=256"
        if user.get("avatar")
        else "https://cdn.discordapp.com/embed/avatars/0.png"
    )

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<style>
body{
    margin:0;height:100vh;
    background:#0b0f1a;
    display:flex;justify-content:center;align-items:center;
    font-family:Segoe UI,sans-serif;color:white;
}
.card{
    background:linear-gradient(135deg,#5865F2,#8b5cf6);
    padding:56px;border-radius:36px;
    text-align:center;
    box-shadow:0 30px 90px rgba(0,0,0,.7);
}
.avatar{
    width:130px;height:130px;
    border-radius:50%;
    border:4px solid white;
}
.name{
    margin-top:16px;
    display:flex;
    justify-content:center;
    gap:10px;
    align-items:center;
    font-size:22px;
}
.dev{
    position:fixed;
    top:22px;right:22px;
    background:#111827;
    padding:16px 20px;
    border-radius:18px;
}
.dev a{
    display:block;
    margin-top:8px;
    background:#1877F2;
    padding:6px 12px;
    border-radius:12px;
    color:white;
    text-decoration:none;
}
</style>
</head>
<body>

<div class="card">
<img src="{{avatar}}" class="avatar">
<div class="name">
<span>{{username}}</span>
<svg width="20" height="20" fill="#22c55e" viewBox="0 0 24 24">
<path d="M12 2l2.39 2.39 3.38-.49.49 3.38L22 12l-2.39 2.39.49 3.38-3.38.49L12 22l-2.39-2.39-3.38.49-.49-3.38L2 12l2.39-2.39-.49-3.38 3.38-.49z"/>
</svg>
</div>
<div style="margin-top:10px;font-weight:700">Verified</div>
</div>

<div class="dev">
<b>Dev Code By Minh Hieu</b>
<a href="https://facebook.com/banlagiv" target="_blank">Facebook</a>
</div>

</body>
</html>
""", username=user["username"], avatar=avatar)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))