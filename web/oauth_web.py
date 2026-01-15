<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Verify Success</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    height: 100vh;
    background: radial-gradient(circle at top, #111827, #020617);
    font-family: 'Segoe UI', Tahoma, sans-serif;
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* ===== VERIFY CARD ===== */
.verify-card {
    background: rgba(17,24,39,.9);
    padding: 34px 40px;
    border-radius: 22px;
    text-align: center;
    box-shadow: 0 0 50px rgba(88,101,242,.55);
    animation: fadeUp .6s ease;
}

.avatar {
    width: 104px;
    height: 104px;
    border-radius: 50%;
    border: 3px solid #5865F2;
    margin-bottom: 14px;
}

.status {
    color: #22c55e;
    font-size: 22px;
    font-weight: 600;
}

.username {
    margin-top: 6px;
    font-size: 16px;
    opacity: .9;
}

.wait {
    margin-top: 10px;
    font-size: 13px;
    opacity: .65;
}

/* ===== DEV CARD ===== */
.dev-card {
    position: fixed;
    top: 16px;
    right: 16px;
    width: 190px;
    padding: 14px;
    border-radius: 16px;
    background: linear-gradient(135deg, #5865F2, #3b82f6);
    box-shadow: 0 14px 30px rgba(0,0,0,.45);
    transition: transform .25s ease, box-shadow .25s ease;
}

.dev-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 22px 45px rgba(0,0,0,.6);
}

.dev-top {
    display: flex;
    align-items: center;
    gap: 8px;
}

.dev-badge {
    width: 22px;
    height: 22px;
    filter: drop-shadow(0 0 6px rgba(255,255,255,.5));
}

.dev-name {
    font-weight: 600;
    font-size: 14px;
}

.dev-sub {
    font-size: 11px;
    opacity: .85;
    margin-top: 2px;
}

.fb-btn {
    display: block;
    margin-top: 10px;
    padding: 7px 0;
    background: #1877F2;
    color: white;
    border-radius: 10px;
    text-align: center;
    text-decoration: none;
    font-size: 12px;
    transition: background .2s ease;
}

.fb-btn:hover {
    background: #0f5ed7;
}

/* ===== TOOLTIP ===== */
.dev-card::after {
    content: "DEV CHÍNH CHỦ";
    position: absolute;
    top: -26px;
    right: 0;
    background: black;
    padding: 4px 8px;
    font-size: 11px;
    border-radius: 6px;
    opacity: 0;
    transition: .25s;
    pointer-events: none;
}

.dev-card:hover::after {
    opacity: 1;
}

/* ===== ANIMATION ===== */
@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(16px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
</head>

<body>

<!-- VERIFY -->
<div class="verify-card">
    <img class="avatar" src="{{ avatar_url }}">
    <div class="status">✔ Xác minh thành công</div>
    <div class="username">{{ username }}</div>
    <div class="wait">Vui lòng chờ admin phê duyệt</div>
</div>

<!-- DEV -->
<div class="dev-card">
    <div class="dev-top">
        <img class="dev-badge"
             src="https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/discord.svg">
        <div>
            <div class="dev-name">Minh Hiếu</div>
            <div class="dev-sub">Discord Developer</div>
        </div>
    </div>

    <a class="fb-btn"
       href="https://facebook.com/banlagiv"
       target="_blank">
        Facebook
    </a>
</div>

</body>
</html>