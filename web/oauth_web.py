from flask import Flask, request, render_template_string
import requests, os

app = Flask(__name__)

# ===== ENV =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GUILD_ID = os.getenv("GUILD_ID")
VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")

OAUTH_URL = (
    "https://discord.com/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    "&response_type=code"
    "&scope=identify"
    f"&redirect_uri={REDIRECT_URI}"
)

# ================= VERIFY PAGE =================
@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Verify</title>
<style>
body{
    margin:0;height:100vh;
    background:radial-gradient(circle at top,#14142b,#07070c);
    display:flex;justify-content:center;align-items:center;
    font-family:system-ui;color:white
}
.box{
    width:380px;
    background:#0f1020;
    border-radius:22px;
    padding:40px;
    box-shadow:0 30px 90px rgba(0,0,0,.8)
}
h1{margin:0 0 10px}
p{color:#a6a8d3;font-size:14px}
a{
    display:block;margin-top:30px;
    padding:15px;border-radius:16px;
    background:linear-gradient(135deg,#5865F2,#9b5cff);
    text-align:center;text-decoration:none;
    color:white;font-weight:600
}
</style>
</head>
<body>
<div class="box">
<h1>Discord Verify</h1>
<p>Xác minh để truy cập server</p>
<a href="{{url}}">Continue with Discord</a>
</div>
</body>
</html>
""", url=OAUTH_URL)

# ================= CALLBACK =================
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Missing code", 400

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
        return f"OAuth2 error: {token}", 400

    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    requests.put(
        f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user['id']}/roles/{VERIFY_ROLE_ID}",
        headers={"Authorization": f"Bot {BOT_TOKEN}"}
    )

    # ================= DASHBOARD CLONE =================
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Dashboard</title>
<style>
body{
    margin:0;
    background:#0b0b10;
    color:white;
    font-family:system-ui;
    display:flex;
}
.sidebar{
    width:260px;
    background:#0f1020;
    padding:28px;
}
.logo{
    font-size:20px;
    font-weight:700;
    margin-bottom:30px;
}
.menu a{
    display:flex;
    align-items:center;
    gap:12px;
    padding:14px 18px;
    margin-bottom:12px;
    border-radius:14px;
    color:#c9c9ff;
    text-decoration:none;
}
.menu a.active{
    background:linear-gradient(135deg,#5865F2,#9b5cff);
    color:white;
}
.main{
    flex:1;
    padding:40px;
}
.card{
    background:#14142b;
    border-radius:22px;
    padding:34px;
    box-shadow:0 25px 70px rgba(0,0,0,.7);
}
.grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
    gap:24px;
    margin-top:30px;
}
.stat{
    background:#101026;
    border-radius:18px;
    padding:24px;
}
.stat h3{margin:0}
.stat small{color:#8e90c8}
</style>
</head>
<body>

<div class="sidebar">
    <div class="logo">RestoreCord</div>
    <div class="menu">
        <a class="active">Dashboard</a>
        <a>Analytics</a>
        <a>Servers</a>
        <a>Verified Members</a>
        <a>Account</a>
    </div>
</div>

<div class="main">
    <div class="card">
        <h1>Welcome, {{name}}</h1>
        <small>Verification completed successfully</small>

        <div class="grid">
            <div class="stat">
                <h3>Verified</h3>
                <small>Status: Active</small>
            </div>
            <div class="stat">
                <h3>Server</h3>
                <small>Access granted</small>
            </div>
            <div class="stat">
                <h3>Security</h3>
                <small>OAuth2 Enabled</small>
            </div>
        </div>
    </div>
</div>

</body>
</html>
""", name=user["username"])

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))