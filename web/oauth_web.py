from flask import Flask, request, render_template_string
import os, requests, urllib.parse, traceback

app = Flask(__name__)

# ======================
# ROUTE HOME
# ======================
@app.route("/")
def index():
    CLIENT_ID = os.getenv("CLIENT_ID")
    REDIRECT_URL = os.getenv("REDIRECT_URL")

    if not CLIENT_ID or not REDIRECT_URL:
        return "❌ Thiếu CLIENT_ID hoặc REDIRECT_URL"

    encoded = urllib.parse.quote(REDIRECT_URL, safe="")
    verify_url = (
        "https://discord.com/api/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={encoded}"
        "&response_type=code"
        "&scope=identify%20guilds.join"
        "&prompt=consent"
    )

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Verify Discord</title>
        <style>
            body{
                margin:0;height:100vh;
                display:flex;justify-content:center;align-items:center;
                background:#0f0f1a;font-family:sans-serif;
            }
            .card{
                background:linear-gradient(135deg,#5865F2,#9b5cff);
                padding:50px 60px;
                border-radius:25px;
                box-shadow:0 15px 40px rgba(0,0,0,.6);
                text-align:center;
                color:white;
            }
            a{
                display:inline-flex;
                gap:10px;
                margin-top:30px;
                padding:16px 36px;
                border-radius:20px;
                background:linear-gradient(45deg,#ff6ec4,#7873f5);
                color:white;
                text-decoration:none;
                font-size:20px;
                font-weight:bold;
                transition:.3s;
            }
            a:hover{
                transform:translateY(-4px) scale(1.05);
            }
            .emoji{
                animation:wiggle 1s infinite;
            }
            @keyframes wiggle{
                0%,100%{transform:rotate(0)}
                25%{transform:rotate(15deg)}
                50%{transform:rotate(-10deg)}
                75%{transform:rotate(10deg)}
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Discord Verify</h1>
            <p>Nhấn nút bên dưới để xác minh</p>
            <a href="{{url}}">
                <span class="emoji">✨</span> Verify
            </a>
        </div>
    </body>
    </html>
    """, url=verify_url)

# ======================
# ROUTE CALLBACK
# ======================
@app.route("/callback")
def callback():
    try:
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        CLIENT_ID = os.getenv("CLIENT_ID")
        CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        GUILD_ID = os.getenv("GUILD_ID")
        VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")
        REDIRECT_URL = os.getenv("REDIRECT_URL")

        if not all([BOT_TOKEN, CLIENT_ID, CLIENT_SECRET, GUILD_ID, VERIFY_ROLE_ID, REDIRECT_URL]):
            return "❌ Thiếu ENV, kiểm tra lại hosting"

        code = request.args.get("code")
        if not code:
            return "❌ Không có code OAuth2"

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

        if "access_token" not in token_res:
            return f"❌ OAuth2 thất bại<br><pre>{token_res}</pre>"

        access_token = token_res["access_token"]

        # Lấy user
        user = requests.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()

        if "id" not in user:
            return f"❌ Không lấy được user<br><pre>{user}</pre>"

        # Gán role
        r = requests.put(
            f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user['id']}/roles/{VERIFY_ROLE_ID}",
            headers={"Authorization": f"Bot {BOT_TOKEN}"}
        )

        if r.status_code not in (200,204):
            return f"❌ Không cấp được role<br><pre>{r.text}</pre>"

        # Thành công
        return render_template_string("""
        <div style="height:100vh;display:flex;justify-content:center;align-items:center;background:#0f0f1a;color:white;font-family:sans-serif">
            <div style="background:linear-gradient(135deg,#43e97b,#38f9d7);padding:50px 70px;border-radius:25px;text-align:center;color:#111">
                <h1>✅ Xác minh thành công</h1>
                <p>Xin chào <b>{{name}}</b></p>
                <a href="https://discord.com/app">Quay lại Discord</a>
            </div>
        </div>
        """, name=user["username"])

    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>"

# ======================
# RUN
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)