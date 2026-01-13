from flask import Flask, request, render_template_string
import requests, os

app = Flask(__name__)

# ENV Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GUILD_ID = os.getenv("GUILD_ID")
VERIFY_ROLE_ID = os.getenv("VERIFY_ROLE_ID")
REDIRECT_URL = os.getenv("REDIRECT_URL")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "❌ Lỗi xác minh"

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
        return "❌ OAuth2 thất bại"

    # Lấy thông tin user
    user = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    ).json()

    # Avatar URL
    avatar_url = f"https://cdn.discordapp.com/avatars/{user['id']}/{user['avatar']}.png?size=256"

    # Cấp role verify
    r = requests.put(
        f"https://discord.com/api/v10/guilds/{GUILD_ID}/members/{user['id']}/roles/{VERIFY_ROLE_ID}",
        headers={"Authorization": f"Bot {BOT_TOKEN}"}
    )
    if r.status_code not in (200, 204):
        return "❌ Không cấp được role"

    # HTML full pro
    html = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>✅ Xác minh thành công</title>
<style>
body {
    margin: 0; padding: 0; height: 100vh;
    display: flex; justify-content: center; align-items: center;
    font-family: 'Segoe UI', Tahoma, sans-serif;
    overflow: hidden;
    background: url('https://cdn.discordapp.com/attachments/1200665203004674088/1460716084213846188/93384E15-2EB0-43E1-94AE-D470EC7E3119.gif?ex=6967ed5d&is=69669bdd&hm=888c4598dec65f4ec00677a0f70f424ce49f256bb9acd2e5f0d52061e99911f0&') center/cover no-repeat;
}
.card {
    background: rgba(0,0,0,0.5);
    padding: 50px 60px;
    border-radius: 20px;
    text-align: center;
    color: white;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
    animation: fadeIn 1s ease forwards;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
}
h1 { font-size: 3em; margin: 0; animation: bounce 1s; }
p { font-size: 1.5em; margin: 0; }
.avatar {
    width: 128px; height: 128px; border-radius: 50%;
    border: 4px solid #ffce00;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    animation: fadeIn 2s ease forwards;
}
/* Button Discord xịn + emoji + animation hover */
a.button {
    text-decoration: none;
    background: #7289da;
    color: white;
    padding: 1em 2em;
    border-radius: 15px;
    font-weight: bold;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    transition: 0.3s transform, 0.3s box-shadow;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-size: 1.2em;
}
a.button:hover {
    transform: translateY(-5px) scale(1.05);
    box-shadow: 0 8px 25px rgba(0,0,0,0.5);
}
a.button span.emoji {
    display: inline-block;
    animation: wiggle 1s infinite;
}
/* Animations */
@keyframes fadeIn { 0% {opacity:0; transform:translateY(-20px);} 100% {opacity:1; transform:translateY(0);} }
@keyframes bounce { 0%,20%,50%,80%,100%{transform:translateY(0);} 40%{transform:translateY(-15px);} 60%{transform:translateY(-8px);} }
@keyframes wiggle {0%,100%{transform:rotate(0deg);}25%{transform:rotate(15deg);}50%{transform:rotate(-10deg);}75%{transform:rotate(10deg);}}
.confetti { position: fixed; width: 10px; height: 10px; background: yellow; animation: confettiFall 3s linear infinite; }
@keyframes confettiFall { 0%{transform:translateY(0) rotate(0deg);} 100%{transform:translateY(100vh) rotate(360deg);} }
</style>
</head>
<body>
<div class="card">
    <img class="avatar" src="{{avatar_url}}" alt="Avatar Discord">
    <h1>✅ Xác minh thành công!</h1>
    <p>Xin chào <b>{{username}}</b></p>
    <a class="button" href="https://discord.com/app">
        <span class="emoji">💖</span> Quay lại Discord
    </a>
</div>

<script>
function createConfetti(){
    for(let i=0;i<30;i++){
        const conf=document.createElement('div');
        conf.className='confetti';
        conf.style.left=Math.random()*100+'vw';
        conf.style.background=`hsl(${Math.random()*360},100%,50%)`;
        conf.style.animationDuration=(Math.random()*2+2)+'s';
        conf.style.width=conf.style.height=(Math.random()*8+4)+'px';
        document.body.appendChild(conf);
        setTimeout(()=>conf.remove(),3000);
    }
}
createConfetti();
</script>

<audio autoplay loop>
    <source src="https://cdn.pixabay.com/download/audio/2023/03/07/audio_ae21c2d2a3.mp3?filename=happy-ukulele-9560.mp3" type="audio/mpeg">
    Trình duyệt của bạn không hỗ trợ audio.
</audio>

</body>
</html>
"""
    return render_template_string(html, username=user["username"], avatar_url=avatar_url)
    
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # port do Render cung cấp
    app.run(host="0.0.0.0", port=port, debug=False)