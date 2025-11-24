from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AxtarGet - Video & Musiqi Endirici</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700;800&display=swap" rel="stylesheet">
    <style>
        * {margin:0;padding:0;box-sizing:border-box;}
        
        :root {
            --bg-primary:#0a0e27;
            --bg-secondary:#1a1f3a;
            --bg-tertiary:#252d48;
            --accent-primary:#00d4ff;
            --accent-secondary:#ff006e;
            --text-primary:#ffffff;
            --text-secondary:#a0aec0;
            --border-color:#404968;
            --success:#10b981;
            --error:#ef4444;
        }
        
        [data-theme="light"] {
            --bg-primary:#f8f9fb;
            --bg-secondary:#ffffff;
            --bg-tertiary:#f3f4f6;
            --accent-primary:#0066ff;
            --accent-secondary:#ff3366;
            --text-primary:#1a202c;
            --text-secondary:#64748b;
            --border-color:#e2e8f0;
        }
        
        body {
            background:linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
            color:var(--text-primary);
            font-family:'Inter',sans-serif;
            min-height:100vh;
            overflow-x:hidden;
            transition:background 0.4s ease;
        }
        
        .container {
            max-width:500px;
            margin:auto;
            padding:40px 24px;
            min-height:100vh;
            display:flex;
            flex-direction:column;
            justify-content:center;
        }
        
        .header {
            text-align:center;
            margin-bottom:50px;
            animation:slideDown 0.6s ease-out;
        }
        
        @keyframes slideDown {
            from {opacity:0;transform:translateY(-30px);}
            to {opacity:1;transform:translateY(0);}
        }
        
        h1 {
            font-family:'Poppins',sans-serif;
            font-size:3.5em;
            font-weight:800;
            background:linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            -webkit-background-clip:text;
            -webkit-text-fill-color:transparent;
            background-clip:text;
            margin-bottom:12px;
            letter-spacing:-1px;
        }
        
        .subtitle {
            font-size:1.1em;
            color:var(--text-secondary);
            font-weight:400;
            letter-spacing:0.3px;
        }
        
        .theme-toggle {
            position:fixed;
            top:24px;
            right:24px;
            width:50px;
            height:50px;
            border-radius:50%;
            background:var(--bg-tertiary);
            border:2px solid var(--border-color);
            cursor:pointer;
            font-size:1.5em;
            display:flex;
            align-items:center;
            justify-content:center;
            transition:all 0.3s ease;
            z-index:999;
        }
        
        .theme-toggle:hover {
            transform:scale(1.1) rotate(20deg);
            border-color:var(--accent-primary);
        }
        
        .tabs {
            display:flex;
            gap:12px;
            margin-bottom:40px;
            animation:slideUp 0.6s ease-out 0.1s both;
        }
        
        @keyframes slideUp {
            from {opacity:0;transform:translateY(30px);}
            to {opacity:1;transform:translateY(0);}
        }
        
        .tab {
            flex:1;
            padding:14px 20px;
            background:var(--bg-tertiary);
            border:2px solid var(--border-color);
            border-radius:12px;
            cursor:pointer;
            font-size:1em;
            color:var(--text-secondary);
            font-weight:600;
            transition:all 0.3s ease;
            position:relative;
            overflow:hidden;
        }
        
        .tab::before {
            content:'';
            position:absolute;
            top:0;
            left:-100%;
            width:100%;
            height:100%;
            background:linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            transition:left 0.4s ease;
            z-index:-1;
        }
        
        .tab.active::before {
            left:0;
        }
        
        .tab.active {
            color:var(--bg-primary);
            border-color:var(--accent-primary);
            font-weight:700;
        }
        
        .tab:hover:not(.active) {
            border-color:var(--accent-primary);
            color:var(--text-primary);
        }
        
        .input-group {
            position:relative;
            margin-bottom:24px;
            animation:slideUp 0.6s ease-out 0.2s both;
        }
        
        input {
            width:100%;
            padding:16px 20px;
            background:var(--bg-tertiary);
            border:2px solid var(--border-color);
            border-radius:14px;
            color:var(--text-primary);
            font-size:1em;
            font-family:'Inter',sans-serif;
            transition:all 0.3s ease;
        }
        
        input::placeholder {
            color:var(--text-secondary);
        }
        
        input:focus {
            outline:none;
            border-color:var(--accent-primary);
            box-shadow:0 0 0 3px rgba(0, 212, 255, 0.1);
            background:var(--bg-secondary);
        }
        
        .button-group {
            animation:slideUp 0.6s ease-out 0.3s both;
        }
        
        button {
            width:100%;
            padding:18px 24px;
            background:linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
            color:var(--bg-primary);
            border:none;
            border-radius:14px;
            font-size:1.1em;
            font-weight:700;
            font-family:'Poppins',sans-serif;
            cursor:pointer;
            transition:all 0.3s ease;
            position:relative;
            overflow:hidden;
            letter-spacing:0.5px;
        }
        
        button::before {
            content:'';
            position:absolute;
            top:50%;
            left:50%;
            width:0;
            height:0;
            border-radius:50%;
            background:rgba(255,255,255,0.3);
            transform:translate(-50%, -50%);
            transition:width 0.6s, height 0.6s;
        }
        
        button:hover::before {
            width:300px;
            height:300px;
        }
        
        button:hover {
            transform:translateY(-3px);
            box-shadow:0 20px 40px rgba(0, 212, 255, 0.3);
        }
        
        button:active {
            transform:translateY(-1px);
        }
        
        button:disabled {
            opacity:0.6;
            cursor:not-allowed;
        }
        
        #status {
            margin-top:28px;
            min-height:60px;
            padding:16px;
            border-radius:12px;
            font-size:1em;
            font-weight:600;
            text-align:center;
            animation:slideUp 0.6s ease-out 0.4s both;
            display:flex;
            align-items:center;
            justify-content:center;
            gap:12px;
        }
        
        .status-hidden {
            display:none !important;
        }
        
        .status-loading {
            background:rgba(0, 212, 255, 0.1);
            border:2px solid var(--accent-primary);
            color:var(--accent-primary);
        }
        
        .status-success {
            background:rgba(16, 185, 129, 0.1);
            border:2px solid var(--success);
            color:var(--success);
        }
        
        .status-error {
            background:rgba(239, 68, 68, 0.1);
            border:2px solid var(--error);
            color:var(--error);
        }
        
        .spinner {
            width:20px;
            height:20px;
            border:3px solid rgba(0, 212, 255, 0.2);
            border-top:3px solid var(--accent-primary);
            border-radius:50%;
            animation:spin 1s linear infinite;
        }
        
        @keyframes spin {
            to {transform:rotate(360deg);}
        }
        
        .icon {
            font-size:1.3em;
        }
        
        @media (max-width:600px) {
            .container {
                padding:30px 16px;
            }
            
            h1 {
                font-size:2.5em;
            }
            
            .subtitle {
                font-size:0.95em;
            }
            
            .tabs {
                gap:10px;
            }
            
            .tab {
                padding:12px 16px;
                font-size:0.95em;
            }
        }
    </style>
</head>
<body>
    <div class="theme-toggle" onclick="toggleTheme()" title="Mövzunu dəyiş">☀️</div>
    
    <div class="container">
        <div class="header">
            <h1>AxtarGet</h1>
            <p class="subtitle">🚀 Filigransız Video & MP3 Endir</p>
        </div>

        <div class="tabs">
            <div class="tab active" onclick="setType('video')">
                📹 Video
            </div>
            <div class="tab" onclick="setType('music')">
                🎵 Musiqi
            </div>
        </div>

        <div class="input-group">
            <input type="text" id="url" placeholder="TikTok, Instagram, YouTube linki yapışdır...">
        </div>
        
        <div class="button-group">
            <button onclick="download()" id="downloadBtn">ENDİR 🔽</button>
        </div>
        
        <div id="status" class="status-hidden"></div>
    </div>

    <script>
        let type = 'video';
        let isDownloading = false;
        
        // Mövzu sistemini yüklə
        const savedTheme = localStorage.getItem('theme') || 'dark';
        document.body.dataset.theme = savedTheme;
        updateThemeIcon();
        
        function toggleTheme() {
            const current = document.body.dataset.theme;
            const newTheme = current === 'dark' ? 'light' : 'dark';
            document.body.dataset.theme = newTheme;
            localStorage.setItem('theme', newTheme);
            updateThemeIcon();
        }
        
        function updateThemeIcon() {
            const icon = document.querySelector('.theme-toggle');
            icon.textContent = document.body.dataset.theme === 'dark' ? '☀️' : '🌙';
        }
        
        function setType(t) {
            type = t;
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            event.target.closest('.tab').classList.add('active');
        }
        
        function showStatus(message, className, withSpinner = false) {
            const status = document.getElementById('status');
            status.className = `${className}`;
            if (withSpinner) {
                status.innerHTML = '<div class="spinner"></div>' + message;
            } else {
                status.innerHTML = message;
            }
        }
        
        async function download() {
            const url = document.getElementById('url').value.trim();
            if (!url) {
                showStatus('⚠️ Zəhmət olmasa link daxil et!', 'status-error');
                return;
            }
            
            if (isDownloading) return;
            isDownloading = true;
            
            const btn = document.getElementById('downloadBtn');
            btn.disabled = true;
            
            showStatus('Video endirilir... 5-10 saniyə gözlə', 'status-loading', true);
            
            try {
                const res = await fetch("/download", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({url, type})
                });
                
                if (res.ok) {
                    const blob = await res.blob();
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = type === 'music' ? 'music.mp3' : 'video.mp4';
                    a.click();
                    showStatus('✅ Uğurla endirildi! Növbəti videonu göndər', 'status-success');
                    document.getElementById('url').value = '';
                } else {
                    showStatus('❌ Xəta oldu. Linki yoxla və ya başqa link sına', 'status-error');
                }
            } catch (err) {
                showStatus('❌ Bağlantı xətası. Zəhmət olmasa yenidən cəhd et', 'status-error');
            } finally {
                isDownloading = false;
                btn.disabled = false;
            }
        }
        
        // Enter tuşu ilə endirmə
        document.getElementById('url').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !isDownloading) {
                download();
            }
        });
    </script>
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    t = data.get("type", "video")
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {'generic': 'impersonate=chrome'},
    }
    if t == "music":
        opts.update({'format': 'bestaudio', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '320'}],'outtmpl': 'out.%(ext)s'})
        ext = "mp3"
    else:
        opts.update({'format': 'best[height<=1080]/best', 'outtmpl': 'out.%(ext)s'})
        ext = "mp4"
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if t == "music": filename = filename.rsplit('.',1)[0] + '.mp3'
        return send_file(filename, as_attachment=True, download_name=("music.mp3" if t=="music" else "video.mp4"))
    except:
        return "Xəta", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
