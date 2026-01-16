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
    margin:0;
    height:100vh;
    background:#0b0f1a;
    display:flex;
    justify-content:center;
    align-items:center;
    font-family:Segoe UI,sans-serif;
    color:white;
}

/* ===== CARD GIỮA ===== */
.card{
    background:linear-gradient(135deg,#5865F2,#7c3aed);
    padding:55px 60px;        /* TO HƠN */
    border-radius:30px;
    text-align:center;
    box-shadow:0 30px 80px rgba(0,0,0,.7);
    max-width:340px;
}

.avatar{
    width:140px;
    height:140px;
    border-radius:50%;
    border:5px solid white;
    margin-bottom:14px;
}

.name{
    display:flex;
    justify-content:center;
    align-items:center;
    gap:8px;
    font-size:22px;
    font-weight:800;
}

.verify-text{
    margin-top:12px;
    font-weight:700;
    font-size:18px;
}

.thank-text{
    margin-top:14px;
    font-size:14px;
    opacity:.9;
}

/* ===== CARD DEV (TO HƠN NỮA) ===== */
.dev{
    position:fixed;
    top:26px;
    right:26px;
    background:linear-gradient(135deg,#111827,#1f2933);
    padding:26px 30px;        /* TO HƠN */
    border-radius:32px;       /* BO GÓC LỚN */
    display:flex;
    align-items:center;
    gap:18px;                 /* GIÃN RỘNG */
    box-shadow:0 28px 80px rgba(0,0,0,.85);
}

.dev img{
    width:72px;               /* AVATAR TO */
    height:72px;
    border-radius:50%;
    border:3px solid #5865F2;
}

.dev-info{
    display:flex;
    flex-direction:column;
}

.dev-name{
    font-weight:900;
    font-size:18px;           /* CHỮ TO */
    letter-spacing:.3px;
}

.dev a{
    margin-top:8px;
    background:#1877F2;
    padding:8px 18px;         /* NÚT TO */
    border-radius:16px;
    color:white;
    text-decoration:none;
    font-size:14px;
    font-weight:600;
    text-align:center;
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
    text-decoration:
}
.dev{
    position:fixed;
    top:24px;
    right:24px;
    background:#111827;
    padding:18px 22px;
    border-radius:22px;
    display:flex;
    align-items:center;
    gap:14px;
    box-shadow:0 16px 50px rgba(0,0,0,.65);
}

.dev img{
    width:56px;
    height:56px;
    border-radius:50%;
}

.dev-name{
    display:flex;
    align-items:center;
    gap:17px;
    font-weight:800;
}

.discord-badge{
    width:22px;
    height:22px;
    background:#5865F2;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
}

.discord-badge svg{
    width:14px;
    height:14px;
    fill:white;
}
</style>
</head>
<body>

<div class="card">
    <img class="avatar" src="{{avatar}}">
    
    <div class="name">
        <span>{{username}}</span>
        <!-- BADGE DISCORD -->
        <svg width="20" height="20" viewBox="0 0 24 24" fill="#22c55e">
            <path d="M12 2.39l2.39 4.85 5.35.78-3.87 3.77.91 5.32L12 14.9l-4.78 2.51.91-5.32-3.87-3.77 5.35-.78L12 2.39z"/>
        </svg>
    </div>

    <div class="verify-text">✔ Xác Minh Thành Công</div>

    <div class="thank-text">
        Cảm ơn bạn đã xác minh<br>
        Bạn có thể quay lại Discord
    </div>
</div>

<div class="dev">
    <img src="https://cdn.discordapp.com/avatars/888766767814553620/6518abba7bc2e7d2ad259fa569298396.png?size=4096size=128">

    <div>
        <div class="dev-name">
            Minh Hieu
            <span class="discord-badge">
                <svg viewBox="0 0 24 24">
                    <path d="M9.999 15.171l-3.88-3.88-1.414 1.414 5.294 5.294L20.7 7.293l-1.414-1.414z"/>
                </svg>
            </span>
        </div>

        <a href="https://facebook.com/banlagiv" target="_blank">Facebook</a>
    </div>
</div>

</body>
</html>
""", username=user["username"], avatar=avatar)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))