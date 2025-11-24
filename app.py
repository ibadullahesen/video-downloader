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
    <style>
        :root {--bg:#000;--card:#111;--text:#fff;--accent:#00ffcc;--accent2:#ff00cc;}
        [data-theme="light"] {--bg:#f8f9fa;--card:#fff;--text:#000;--accent:#007bff;--accent2:#ff6b6b;}
        body {background:var(--bg);color:var(--text);font-family:'Segoe UI',sans-serif;margin:0;padding:20px;transition:0.4s;}
        .container {max-width:850px;margin:auto;background:var(--card);padding:40px;border-radius:25px;box-shadow:0 10px 40px rgba(0,255,255,0.2);}
        h1 {font-size:3em;background:linear-gradient(45deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
        .theme {position:fixed;top:20px;right:20px;font-size:2em;cursor:pointer;z-index:999;}
        .tabs {display:flex;justify-content:center;gap:20px;margin:30px 0;}
        .tab {padding:15px 35px;background:#222;border-radius:50px;cursor:pointer;transition:0.3s;}
        .tab.active {background:var(--accent);color:#000;font-weight:bold;}
        input {width:80%;padding:18px;border:none;border-radius:50px;background:#222;color:#fff;font-size:1.1em;margin:20px 0;}
        button {padding:18px 50px;background:var(--accent);color:#000;border:none;border-radius:50px;font-size:1.3em;cursor:pointer;font-weight:bold;transition:0.3s;}
        button:hover {transform:scale(1.05);}
        #status {margin-top:25px;font-size:1.4em;font-weight:bold;min-height:50px;}
        .success {color:#00ff88;animation:pulse 1s infinite;}
        @keyframes pulse {0%,100%{opacity:1;}50%{opacity:0.7;}}
    </style>
</head>
<body>
    <div class="theme" onclick="document.body.dataset.theme=document.body.dataset.theme==='light'?'':'light'">☀️</div>
    <div class="container">
        <h1>AxtarGet</h1>
        <p style="font-size:1.3em;color:#aaa;">Filigransız Video & MP3 Endir</p>

        <div class="tabs">
            <div class="tab active" onclick="setType('video')">Video</div>
            <div class="tab" onclick="setType('music')">Musiqi</div>
        </div>

        <input type="text" id="url" placeholder="TikTok, Instagram, YouTube linki yapışdır...">
        <button onclick="download()">ENDİR</button>
        <div id="status"></div>
    </div>

    <script>
        let type = 'video';
        function setType(t) { type=t; document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active')); event.target.classList.add('active'); }
        async function download() {
            const url = document.getElementById('url').value.trim();
            if (!url) return alert("Link daxil et!");
            const status = document.getElementById('status');
            status.innerHTML = "5 saniyə gözlə… Video endirilir";
            status.className = "";
            
            const res = await fetch("/download", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url,type})});
            if (res.ok) {
                const blob = await res.blob();
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = type==='music'?'music.mp3':'video.mp4';
                a.click();
                status.innerHTML = "Uğurla endirildi! Növbəti videonu göndər";
                status.className = "success";
            } else {
                status.innerHTML = "Xəta oldu. Linki yoxla və ya başqa link sına.";
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
