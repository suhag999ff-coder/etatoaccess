import os
import urllib.parse
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ===================================================================
# REAL GARENA API LOGIC (EXACTLY FROM BOT.PY)
# ===================================================================
def eat_to_access_token(eat_input):
    eat_token = None
    eat_input = eat_input.strip()

    # Extract EAT parameter if full URL is given
    if "http" in eat_input or "?" in eat_input:
        parsed_url = urllib.parse.urlparse(eat_input)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if 'eat' in query_params:
            eat_token = query_params['eat'][0]
        elif 'access_token' in query_params:
            eat_token = query_params['access_token'][0]
    else:
        eat_token = eat_input

    if not eat_token:
        return False, "Could not find a valid EAT token in your input.", {}

    # Official Garena OTRSS callback endpoint (same as bot.py)
    api_url = f"https://api-otrss.garena.com/support/callback/?access_token={eat_token}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/536.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/536.36"
    }

    try:
        response = requests.get(api_url, headers=headers, allow_redirects=True, timeout=15)
        parsed = urllib.parse.urlparse(response.url)
        params = urllib.parse.parse_qs(parsed.query)

        if 'access_token' in params:
            access_token = params['access_token'][0]
            account_id = params.get('account_id', ['Unknown'])[0]
            raw_nickname = params.get('nickname', ['Unknown'])[0]
            nickname = urllib.parse.unquote(raw_nickname)
            region = params.get('region', ['Unknown'])[0]

            return True, "Conversion successful", {
                "access_token": access_token,
                "account_id": account_id,
                "nickname": nickname,
                "region": region
            }
        else:
            return False, "Token expired or invalid! Server did not return access credentials.", {}
    except Exception as e:
        return False, f"Connection error: {str(e)}", {}


# ===================================================================
# API ROUTE FOR FRONTEND CONVERSION
# ===================================================================
@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.get_json() or {}
    credential = data.get('credential', '').strip()

    if not credential:
        return jsonify({"success": False, "error": "Please enter an EAT Token or URL!"}), 400

    success, msg, result = eat_to_access_token(credential)
    if success:
        return jsonify({
            "success": True,
            "data": result
        })
    else:
        return jsonify({
            "success": False,
            "error": msg
        }), 400


# ===================================================================
# EMBEDDED FRONTEND HTML / CSS / JS (KILLER SHARMA / NOYON UI)
# ===================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ACCESS GENERATOR | by Noyon (@w8noyon)</title>
    <!-- FontAwesome 6 & Google Fonts -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">

    <style>
        :root {
            --bg-base: #050209;
            --card-bg: #090412;
            --card-border: rgba(168, 85, 247, 0.2);
            --card-subtle-bg: rgba(22, 10, 36, 0.6);
            --primary-pink: #ec4899;
            --primary-purple: #c026d3;
            --neon-pink-glow: rgba(236, 72, 153, 0.45);
            --text-primary: #ffffff;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --green-status: #10b981;
            --grid-line: rgba(168, 85, 247, 0.05);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--bg-base);
            background-image: 
                linear-gradient(to right, var(--grid-line) 1px, transparent 1px),
                linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px),
                radial-gradient(circle at 50% 0%, rgba(192, 38, 211, 0.18) 0%, transparent 60%),
                radial-gradient(circle at 50% 100%, rgba(236, 72, 153, 0.12) 0%, transparent 50%);
            background-size: 26px 26px, 26px 26px, 100% 100%, 100% 100%;
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 24px 12px 60px;
        }

        .page-wrapper {
            width: 100%;
            max-width: 425px;
        }

        .card-container {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 36px;
            padding: 30px 20px;
            box-shadow: 0 0 50px rgba(0, 0, 0, 0.95), 0 0 35px rgba(168, 85, 247, 0.08);
            position: relative;
            overflow: hidden;
        }

        .card-container::before {
            content: '';
            position: absolute;
            top: -100px;
            left: 50%;
            transform: translateX(-50%);
            width: 220px;
            height: 220px;
            background: radial-gradient(circle, rgba(236, 72, 153, 0.22) 0%, transparent 70%);
            pointer-events: none;
        }

        /* Profile Section */
        .profile-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            margin-bottom: 24px;
        }

        .avatar-wrapper {
            width: 88px;
            height: 88px;
            border-radius: 50%;
            border: 2.5px solid var(--primary-pink);
            padding: 3px;
            box-shadow: 0 0 22px var(--neon-pink-glow), inset 0 0 12px var(--neon-pink-glow);
            margin-bottom: 14px;
            background: #000;
            overflow: hidden;
            animation: pulseLogo 3s infinite ease-in-out;
        }

        @keyframes pulseLogo {
            0%, 100% { box-shadow: 0 0 18px var(--neon-pink-glow); border-color: var(--primary-pink); }
            50% { box-shadow: 0 0 28px rgba(192, 38, 211, 0.85); border-color: #c026d3; }
        }

        .avatar-img {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            object-fit: cover;
        }

        .main-title {
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.85rem;
            font-weight: 700;
            letter-spacing: 1.5px;
            color: #ffffff;
            text-shadow: 0 0 15px rgba(255, 255, 255, 0.2);
            margin-bottom: 4px;
        }

        .subtitle {
            font-size: 0.88rem;
            color: var(--primary-pink);
            font-weight: 500;
            letter-spacing: 0.4px;
        }

        /* Tutorial Cards */
        .tutorials-group {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 22px;
        }

        .tutorial-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1.5px dashed rgba(192, 38, 211, 0.75);
            border-radius: 20px;
            padding: 13px 18px;
            text-decoration: none;
            color: inherit;
            background: rgba(22, 10, 36, 0.45);
            transition: all 0.25s ease;
        }

        .tutorial-card:hover {
            border-color: var(--primary-pink);
            box-shadow: 0 0 16px rgba(236, 72, 153, 0.25);
            transform: translateY(-1px);
        }

        .tut-left {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .tut-icon-box i {
            color: #ff0033;
            font-size: 1.65rem;
        }

        .tut-texts {
            display: flex;
            flex-direction: column;
        }

        .tut-title {
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.8px;
            color: #ffffff;
        }

        .tut-desc {
            font-size: 0.76rem;
            color: #a78bfa;
        }

        .tut-arrow {
            color: #c084fc;
            font-size: 1.05rem;
        }

        /* How to Use Card */
        .how-to-use-card {
            background: var(--card-subtle-bg);
            border: 1px solid rgba(168, 85, 247, 0.2);
            border-radius: 22px;
            padding: 20px 18px;
            margin-bottom: 22px;
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 18px;
        }

        .book-icon {
            color: var(--primary-pink);
            font-size: 1.25rem;
        }

        .card-header h2 {
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.22rem;
            font-weight: 700;
            letter-spacing: 0.8px;
        }

        .step-item {
            display: flex;
            gap: 14px;
            margin-bottom: 16px;
        }

        .step-item:last-child {
            margin-bottom: 0;
        }

        .step-badge {
            width: 26px;
            height: 26px;
            border-radius: 8px;
            background: #581c87;
            color: #ffffff;
            font-weight: 700;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .step-content {
            flex: 1;
        }

        .step-title {
            font-size: 0.85rem;
            line-height: 1.4;
            color: #e2e8f0;
            margin-bottom: 6px;
        }

        .safety-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.76rem;
            color: var(--green-status);
            font-weight: 500;
        }

        .eat-highlight {
            color: var(--primary-pink);
            font-weight: 700;
            font-family: 'Fira Code', monospace;
        }

        .code-example-box {
            background: #06020a;
            border: 1px solid rgba(168, 85, 247, 0.22);
            border-radius: 10px;
            padding: 8px 12px;
            margin: 8px 0;
        }

        .example-label {
            font-size: 0.68rem;
            color: var(--text-muted);
            display: block;
            margin-bottom: 3px;
        }

        .example-code {
            font-family: 'Fira Code', monospace;
            font-size: 0.72rem;
            color: #c084fc;
            word-break: break-all;
            line-height: 1.35;
        }

        .step-footnote {
            font-size: 0.74rem;
            color: var(--text-muted);
        }

        /* Provider Icons Grid */
        .provider-section {
            margin-bottom: 18px;
        }

        .section-label {
            font-family: 'Rajdhani', sans-serif;
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.8px;
            margin-bottom: 10px;
            color: #f1f5f9;
        }

        .providers-row {
            display: flex;
            justify-content: space-between;
            gap: 8px;
        }

        /* RGB Lighting Buttons */
        .rgb-btn {
            position: relative;
            z-index: 1;
            overflow: hidden;
            transition: all 0.25s ease;
        }

        .rgb-btn::before {
            content: '';
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: conic-gradient(#ff0055, #ffbe0b, #00f0ff, #00ff66, #ff0055);
            opacity: 0;
            z-index: -2;
            transition: opacity 0.3s;
            animation: rgbRotate 2.5s linear infinite;
        }

        .rgb-btn::after {
            content: '';
            position: absolute;
            inset: 2px;
            background: #0d0718;
            border-radius: inherit;
            z-index: -1;
        }

        .rgb-btn:active::before,
        .rgb-btn.rgb-active::before {
            opacity: 1;
        }

        .rgb-btn:active,
        .rgb-btn.rgb-active {
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.6), 0 0 35px rgba(255, 0, 85, 0.4);
            transform: scale(0.97);
        }

        @keyframes rgbRotate {
            100% { transform: rotate(360deg); }
        }

        .provider-btn {
            flex: 1;
            height: 48px;
            border: 1px solid rgba(168, 85, 247, 0.25);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            font-size: 1.25rem;
            color: #ffffff;
        }

        .provider-btn.google { color: #ea4335; }
        .provider-btn.facebook { color: #1877f2; }
        .provider-btn.apple { color: #ffffff; }
        .provider-btn.x-twitter { color: #f8fafc; }
        .provider-btn.vk { color: #2787f5; }

        /* Input Field */
        .input-section {
            margin-bottom: 14px;
        }

        .input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
        }

        .input-icon {
            position: absolute;
            left: 14px;
            color: var(--text-muted);
            font-size: 0.95rem;
            pointer-events: none;
        }

        .custom-input {
            width: 100%;
            height: 52px;
            background: #07030e;
            border: 1px solid rgba(168, 85, 247, 0.28);
            border-radius: 14px;
            padding: 0 42px 0 38px;
            color: #ffffff;
            font-size: 0.88rem;
            outline: none;
            transition: border-color 0.25s, box-shadow 0.25s;
        }

        .custom-input:focus {
            border-color: var(--primary-pink);
            box-shadow: 0 0 14px rgba(236, 72, 153, 0.35);
        }

        .custom-input::placeholder {
            color: #64748b;
        }

        .clear-btn {
            position: absolute;
            right: 12px;
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 1rem;
            cursor: pointer;
            padding: 4px;
        }

        .clear-btn:hover {
            color: #fff;
        }

        .input-hint {
            display: block;
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 5px;
            padding-left: 4px;
        }

        /* Action Button */
        .generate-btn {
            width: 100%;
            height: 54px;
            background: linear-gradient(90deg, #9333ea 0%, #d946ef 50%, #ec4899 100%);
            border: none;
            border-radius: 16px;
            color: #ffffff;
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: 1.5px;
            cursor: pointer;
            box-shadow: 0 0 24px rgba(217, 70, 239, 0.45);
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
        }

        .generate-btn:hover:not(:disabled) {
            box-shadow: 0 0 30px rgba(236, 72, 153, 0.65);
            transform: scale(1.01);
        }

        .generate-btn.rgb-active {
            box-shadow: 0 0 35px #ff0055, 0 0 50px #00f0ff, 0 0 65px #ffbe0b !important;
            animation: rgbFlash 0.6s ease-in-out;
        }

        @keyframes rgbFlash {
            0% { filter: hue-rotate(0deg) brightness(1.3); }
            50% { filter: hue-rotate(180deg) brightness(1.8); }
            100% { filter: hue-rotate(360deg) brightness(1); }
        }

        .generate-btn:disabled {
            opacity: 0.65;
            cursor: not-allowed;
        }

        .loader-spinner {
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* Result Card */
        .result-card {
            background: #090312;
            border: 1px solid rgba(236, 72, 153, 0.35);
            border-radius: 20px;
            padding: 18px;
            margin-bottom: 22px;
            box-shadow: 0 0 25px rgba(236, 72, 153, 0.18);
            animation: slideDown 0.3s ease-out;
        }

        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
        }

        .badge-success {
            font-family: 'Rajdhani', sans-serif;
            font-size: 0.98rem;
            font-weight: 700;
            color: var(--green-status);
            letter-spacing: 1px;
        }

        .close-card-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            cursor: pointer;
            font-size: 1rem;
        }

        .account-info-box {
            background: #0e061a;
            border: 1px solid rgba(168, 85, 247, 0.15);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 14px;
        }

        .info-row {
            display: flex;
            font-size: 0.85rem;
            margin-bottom: 6px;
        }

        .info-row:last-child {
            margin-bottom: 0;
        }

        .info-label {
            width: 70px;
            color: var(--text-secondary);
        }

        .info-colon {
            width: 15px;
            color: var(--text-muted);
        }

        .info-value {
            flex: 1;
            font-weight: 600;
            color: #ffffff;
        }

        .info-value.text-accent { color: #f472b6; }
        .info-value.text-green { color: var(--green-status); }
        .info-value.font-mono { font-family: 'Fira Code', monospace; }

        .access-token-box {
            margin-bottom: 14px;
        }

        .token-title {
            font-family: 'Rajdhani', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.8px;
            color: var(--text-secondary);
            display: block;
            margin-bottom: 6px;
        }

        .token-value-wrap {
            background: #040108;
            border: 1px dashed rgba(168, 85, 247, 0.35);
            border-radius: 10px;
            padding: 10px 12px;
            max-height: 80px;
            overflow-y: auto;
        }

        .token-value-wrap code {
            font-family: 'Fira Code', monospace;
            font-size: 0.76rem;
            color: #ec4899;
            word-break: break-all;
        }

        .copy-action-btn {
            width: 100%;
            height: 44px;
            background: rgba(192, 38, 211, 0.2);
            border: 1px solid var(--primary-pink);
            border-radius: 10px;
            color: #ffffff;
            font-family: 'Rajdhani', sans-serif;
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 1px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s;
        }

        .copy-action-btn:hover {
            background: var(--primary-pink);
            box-shadow: 0 0 15px var(--neon-pink-glow);
        }

        /* Social Connections */
        .social-section {
            text-align: center;
            margin-bottom: 20px;
        }

        .social-title {
            font-family: 'Rajdhani', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            letter-spacing: 0.8px;
            color: var(--text-secondary);
            display: block;
            margin-bottom: 12px;
        }

        .social-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }

        .social-btn {
            background: #0d0718;
            border: 1px solid rgba(168, 85, 247, 0.15);
            border-radius: 14px;
            padding: 12px 14px;
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            color: #ffffff;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .social-btn:hover {
            border-color: rgba(168, 85, 247, 0.5);
            transform: translateY(-2px);
            background: #150b26;
        }

        .telegram-color { color: #229ed9; font-size: 1.15rem; }
        .youtube-color { color: #ff0000; font-size: 1.15rem; }
        .instagram-color { color: #e1306c; font-size: 1.15rem; }
        .whatsapp-color { color: #25d366; font-size: 1.15rem; }

        .footer {
            text-align: center;
        }

        .terms-link {
            font-size: 0.76rem;
            color: var(--text-muted);
            text-decoration: underline;
        }

        /* Toast Alert */
        .toast {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: #180829;
            border: 1px solid var(--primary-pink);
            color: #ffffff;
            padding: 10px 22px;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: 0 0 20px var(--neon-pink-glow);
            transition: transform 0.3s cubic-bezier(0.18, 0.89, 0.32, 1.28);
            z-index: 1000;
            pointer-events: none;
        }

        .toast.show {
            transform: translateX(-50%) translateY(0);
        }
    </style>
</head>
<body>

<div class="page-wrapper">
    <div class="card-container">
        
        <!-- Profile Header -->
        <div class="profile-section">
            <div class="avatar-wrapper">
                <img src="https://i.ibb.co/23FJjtLw/c1b2dd7a2d36.jpg" alt="Logo" class="avatar-img">
            </div>
            <h1 class="main-title">ACCESS GENERATOR</h1>
            <p class="subtitle">by Noyon (@w8noyon)</p>
        </div>

        <!-- Tutorials Group -->
        <div class="tutorials-group">
            <a href="https://youtu.be/Ql0oNbteQoc?si=ivW7uEwXbdpZe4NT" target="_blank" rel="noopener noreferrer" class="tutorial-card rgb-btn">
                <div class="tut-left">
                    <div class="tut-icon-box">
                        <i class="fa-brands fa-youtube"></i>
                    </div>
                    <div class="tut-texts">
                        <span class="tut-title">FULL TUTORIAL</span>
                        <span class="tut-desc">click to watch how to get eat token</span>
                    </div>
                </div>
                <i class="fa-solid fa-arrow-right tut-arrow"></i>
            </a>

            <a href="https://youtube.com/@noyonofficial99?si=TMqH1oeoADaEpJZI" target="_blank" rel="noopener noreferrer" class="tutorial-card rgb-btn">
                <div class="tut-left">
                    <div class="tut-icon-box">
                        <i class="fa-brands fa-youtube"></i>
                    </div>
                    <div class="tut-texts">
                        <span class="tut-title">2ND METHOD</span>
                        <span class="tut-desc">click to watch how to get access token</span>
                    </div>
                </div>
                <i class="fa-solid fa-arrow-right tut-arrow"></i>
            </a>
        </div>

        <!-- How To Use -->
        <div class="how-to-use-card">
            <div class="card-header">
                <i class="fa-solid fa-book-open book-icon"></i>
                <h2>HOW TO USE</h2>
            </div>

            <div class="step-item">
                <div class="step-badge">1</div>
                <div class="step-content">
                    <p class="step-title">Select Provider & Login below.</p>
                    <div class="safety-tag">
                        <i class="fa-solid fa-circle-check"></i>
                        <span>Safe: Official Garena Server (No Scam Risk!)</span>
                    </div>
                </div>
            </div>

            <div class="step-item">
                <div class="step-badge">2</div>
                <div class="step-content">
                    <p class="step-title">After login, copy the URL containing <span class="eat-highlight">eat=</span> parameter</p>
                    
                    <div class="code-example-box">
                        <span class="example-label">Example URL:</span>
                        <div class="example-code">https://discstore.kiosgamer.com.id/?eat=14f060774299fb93a5...&lang=en&ion=IND&account_id=7669969208&nickname=...</div>
                    </div>
                    <p class="step-footnote">The tool will extract the eat token automatically</p>
                </div>
            </div>

            <div class="step-item">
                <div class="step-badge">3</div>
                <div class="step-content">
                    <p class="step-title">Paste the URL or just the <b>Eat Token</b> below and click <b>GENERATE</b></p>
                </div>
            </div>
        </div>

        <!-- Provider Login Selection -->
        <div class="provider-section">
            <h3 class="section-label">SELECT PROVIDER & LOGIN</h3>
            <div class="providers-row">
                <a href="https://auth.garena.com/universal/oauth?platform=8&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/" target="_blank" rel="noopener noreferrer" class="provider-btn google rgb-btn" title="Google">
                    <i class="fa-brands fa-google"></i>
                </a>
                <a href="https://auth.garena.com/universal/oauth?platform=3&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/" target="_blank" rel="noopener noreferrer" class="provider-btn facebook rgb-btn" title="Facebook">
                    <i class="fa-brands fa-facebook-f"></i>
                </a>
                <a href="https://auth.garena.com/universal/oauth?platform=10&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/" target="_blank" rel="noopener noreferrer" class="provider-btn apple rgb-btn" title="Apple / iCloud">
                    <i class="fa-brands fa-apple"></i>
                </a>
                <a href="https://auth.garena.com/universal/oauth?platform=11&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/" target="_blank" rel="noopener noreferrer" class="provider-btn x-twitter rgb-btn" title="Twitter / X">
                    <i class="fa-brands fa-x-twitter"></i>
                </a>
                <a href="https://auth.garena.com/universal/oauth?platform=5&response_type=code&locale=en-SG&client_id=100067&redirect_uri=https://api.ff.garena.co.id/auth/auth/callback_n?site=https://api-discountstore.kiosgamer.gameid.garena.co.id/oauth/callback_redirect/" target="_blank" rel="noopener noreferrer" class="provider-btn vk rgb-btn" title="VK">
                    <i class="fa-brands fa-vk"></i>
                </a>
            </div>
        </div>

        <!-- Input Area -->
        <div class="input-section">
            <div class="input-wrapper">
                <i class="fa-solid fa-link input-icon"></i>
                <input type="text" id="credentialInput" class="custom-input" placeholder="Paste kiosgamer URL or Eat Token" autocomplete="off" spellcheck="false">
                <button type="button" id="clearBtn" class="clear-btn" title="Clear input" style="display: none;">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>
            <span class="input-hint">Supports full URL or raw token</span>
        </div>

        <!-- Action Button -->
        <button type="button" id="generateBtn" class="generate-btn">
            <span class="btn-text">GENERATE ACCESS &rarr;</span>
            <div class="loader-spinner" style="display: none;"></div>
        </button>

        <!-- Result Box -->
        <div id="resultCard" class="result-card" style="display: none;">
            <div class="result-header">
                <span class="badge-success">ACCESS GENERATED &#10003;</span>
                <button type="button" id="closeResultBtn" class="close-card-btn" title="Close"><i class="fa-solid fa-xmark"></i></button>
            </div>

            <div class="account-info-box">
                <div class="info-row">
                    <span class="info-label">Name</span>
                    <span class="info-colon">:</span>
                    <span class="info-value text-accent" id="resName">--</span>
                </div>
                <div class="info-row">
                    <span class="info-label">UID</span>
                    <span class="info-colon">:</span>
                    <span class="info-value font-mono" id="resUID">--</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Region</span>
                    <span class="info-colon">:</span>
                    <span class="info-value" id="resRegion">--</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Account</span>
                    <span class="info-colon">:</span>
                    <span class="info-value text-green" id="resAccount">Verified &#10003;</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Status</span>
                    <span class="info-colon">:</span>
                    <span class="info-value text-green" id="resStatus">Active</span>
                </div>
            </div>

            <div class="access-token-box">
                <span class="token-title">ACCESS RESULT</span>
                <div class="token-value-wrap">
                    <code id="resToken">--</code>
                </div>
            </div>

            <button type="button" id="copyResultBtn" class="copy-action-btn rgb-btn">
                <i class="fa-regular fa-copy"></i>
                <span>COPY RESULT</span>
            </button>
        </div>

        <!-- Social Connections -->
        <div class="social-section">
            <span class="social-title">CONNECT WITH NOYON (@W8NOYON)</span>
            <div class="social-grid">
                <a href="https://t.me/w8noyon" target="_blank" rel="noopener noreferrer" class="social-btn">
                    <i class="fa-brands fa-telegram telegram-color"></i>
                    <span>Telegram</span>
                </a>
                <a href="https://youtube.com/@noyonofficial99?si=TMqH1oeoADaEpJZI" target="_blank" rel="noopener noreferrer" class="social-btn">
                    <i class="fa-brands fa-youtube youtube-color"></i>
                    <span>YouTube</span>
                </a>
                <a href="https://www.instagram.com/__ur_suhag__?stkn=MWY4YzY5OHBhZTFwMw==" target="_blank" rel="noopener noreferrer" class="social-btn">
                    <i class="fa-brands fa-instagram instagram-color"></i>
                    <span>Instagram</span>
                </a>
                <a href="https://wa.me/8801717897877" target="_blank" rel="noopener noreferrer" class="social-btn">
                    <i class="fa-brands fa-whatsapp whatsapp-color"></i>
                    <span>WhatsApp</span>
                </a>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <a href="#terms" class="terms-link">Terms & Conditions</a>
        </div>

    </div>
</div>

<div id="toast" class="toast">Action completed</div>

<script>
    document.addEventListener('DOMContentLoaded', () => {
        const credentialInput = document.getElementById('credentialInput');
        const clearBtn = document.getElementById('clearBtn');
        const generateBtn = document.getElementById('generateBtn');
        const btnText = generateBtn.querySelector('.btn-text');
        const btnSpinner = generateBtn.querySelector('.loader-spinner');

        const resultCard = document.getElementById('resultCard');
        const resName = document.getElementById('resName');
        const resUID = document.getElementById('resUID');
        const resRegion = document.getElementById('resRegion');
        const resAccount = document.getElementById('resAccount');
        const resStatus = document.getElementById('resStatus');
        const resToken = document.getElementById('resToken');
        const copyResultBtn = document.getElementById('copyResultBtn');
        const closeResultBtn = document.getElementById('closeResultBtn');
        const toast = document.getElementById('toast');

        // RGB Lighting trigger
        document.querySelectorAll('.rgb-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                this.classList.add('rgb-active');
                setTimeout(() => this.classList.remove('rgb-active'), 800);
            });
        });

        credentialInput.addEventListener('input', () => {
            clearBtn.style.display = credentialInput.value.trim() ? 'block' : 'none';
        });

        clearBtn.addEventListener('click', () => {
            credentialInput.value = '';
            clearBtn.style.display = 'none';
            credentialInput.focus();
        });

        closeResultBtn.addEventListener('click', () => {
            resultCard.style.display = 'none';
        });

        copyResultBtn.addEventListener('click', () => {
            const token = resToken.textContent;
            if (!token || token === '--') return;
            navigator.clipboard.writeText(token).then(() => {
                showToast('Access Token copied to clipboard!');
            });
        });

        function showToast(msg) {
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2500);
        }

        // Real API Trigger Function
        generateBtn.addEventListener('click', async () => {
            const raw = credentialInput.value.trim();

            generateBtn.classList.add('rgb-active');
            setTimeout(() => generateBtn.classList.remove('rgb-active'), 900);

            if (!raw) {
                showToast('Please paste a URL or Eat Token first!');
                credentialInput.focus();
                return;
            }

            generateBtn.disabled = true;
            btnText.textContent = 'GENERATING...';
            btnSpinner.style.display = 'block';
            resultCard.style.display = 'none';

            try {
                // Call Python backend endpoint which executes the real Garena API
                const res = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ credential: raw })
                });

                const data = await res.json();

                if (!res.ok || !data.success) {
                    throw new Error(data.error || 'Failed to extract token');
                }

                const result = data.data;

                // Set Real Info from Garena
                resName.textContent = result.nickname || 'Unknown';
                resUID.textContent = result.account_id || 'Unknown';
                resRegion.textContent = result.region || 'Unknown';
                resAccount.textContent = 'Verified ✓';
                resStatus.textContent = 'Active';
                resToken.textContent = result.access_token || 'None';

                resultCard.style.display = 'block';
                showToast('Real Access Token Generated!');
            } catch (err) {
                showToast(err.message || 'Error occurred!');
            } finally {
                generateBtn.disabled = false;
                btnText.textContent = 'GENERATE ACCESS →';
                btnSpinner.style.display = 'none';
            }
        });
    });
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    print("🚀 Noyon Official Access Generator Server Running!")
    print("👉 Open your browser: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)