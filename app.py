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
    <title>AxtarGet - Video & Musiqi Endir</title>
    <style>
        :root { --bg: #000; --fg: #fff; --card: #111; --accent: #00ffcc; }
        [data-theme="light"] { --bg: #fff; --fg: #000; --card: #f9f9f9; --accent: #007bff; }
        body {font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--fg); text-align: center; padding: 20px; margin:0; transition: 0.3s;}
        .container {max-width: 800px; margin: auto; padding: 30px; background: var(--card); border-radius: 20px; box-shadow: 0 0 30px rgba(0,255,255,0.2); transition: 0.3s;}
        h1 {font-size: 2.5em; margin-bottom: 10px; background: linear-gradient(45deg,var(--accent),#ff00cc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
        .tabs {display: flex; justify-content: center; margin: 30px 0;}
        .tab {padding: 15px 30px; background: #222; margin: 0 10px; border-radius: 50px; cursor: pointer; transition: 0.3s;}
        .tab.active {background: var(--accent); color: var(--bg); font-weight: bold;}
        input {width: 80%; padding: 15px; margin: 20px 0; border: none; border-radius: 50px; font-size: 1.1em; background: #222; color: var(--fg);}
        button {padding: 15px 40px; background: var(--accent); color: var(--bg); border: none; border-radius: 50px; font-size: 1.2em; cursor: pointer; font-weight: bold; transition: 0.3s;}
        #result {margin-top: 20px; font-size: 1.3em; animation: pulse 1.5s infinite;}
        @keyframes pulse {0%,100%{opacity:1;}50%{opacity:0.5;}}
        .theme-toggle {position: fixed; top: 20px; right: 20px; padding: 10px; background: var(--accent); border-radius: 50px; cursor: pointer;}
        .footer {margin-top: 50px; color: #666; font-size: 0.9em;}
    </style>
</head>
<body>
    <div class="theme-toggle" onclick="toggleTheme()">🌙/☀</div>
    <div class="container">
        <h1>AxtarGet</h1>
        <p>Filigransız Video & MP3 Endir</p>
        
        <div class="tabs">
            <div class="tab active" onclick="show('video')">🎬 Video</div>
            <div class="tab" onclick="show('music')">🎵 Musiqi</div>
        </div>

        <input type="text" id="url" placeholder="TikTok, Instagram, YouTube linki yapışdır...">
        <button onclick="download()">⬇ ENDİR</button>
        <div id="result"></div>
    </div>

    <script>
        function toggleTheme() {
            document.body.dataset.theme = document.body.dataset.theme === 'light' ? 'dark' : 'light';
        }
        function show(type) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            window.currentType = type;
        }
        window.currentType = 'video';

        async function download() {
            const url = document.getElementById('url').value;
            if (!url) return alert("Link daxil et!");
            const result = document.getElementById('result');
            result.innerHTML = "🔄 5 saniyə gözlə... Video/Musiqi endirilir...";
            
            const res = await fetch("/download", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({url: url, type: window.currentType})
            });
            
            if (res.ok) {
                const blob = await res.blob();
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = window.currentType === 'music' ? "music.mp3" : "video.mp4";
                a.click();
                result.innerHTML = "✅ Uğurla endirildi!";
            } else {
                result.innerHTML = "❌ Xəta oldu. Linki yoxla və ya başqa link sına.";
            }
        }
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
    type_ = data.get("type", "video")

    if type_ == "music":
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': 'audio.%(ext)s',
            'quiet': True,
            'extractor_args': {'generic': 'impersonate=chrome'},
        }
        filename_ext = "mp3"
    else:
        ydl_opts = {
            'format': 'best[height<=1080]/best',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
            'extractor_args': {'generic': 'impersonate=chrome'},
        }
        filename_ext = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.' + filename_ext
        return send_file(filename, as_attachment=True, download_name=( "music.mp3" if type_ == "music" else "video.mp4" ))
    except Exception as e:
        return f"Xəta: {str(e)}", 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
