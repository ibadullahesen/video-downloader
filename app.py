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
    <title>AxtarGet – Video & MP3</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root{--bg:#0d0b1c;--card:#15132b;--accent:#00f5ff;--accent2:#ff00aa;--text:#e0e0ff;--border:#2a265f;--glow:0 0 20px rgba(0,245,255,0.4);}
        [data-theme=light]{--bg:#f5f7ff;--card:#ffffff;--accent:#0066ff;--accent2:#ff006e;--text:#1a1a2e;--border:#e0e0ff;--glow:0 0 20px rgba(0,102,255,0.3);}
        *{margin:0;padding:0;box-sizing:border-box;}
        body{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;display:flex;min-height:100dvh;align-items:center;justify-content:center;padding:20px;transition:all .4s;background:radial-gradient(circle at 50% 50%,rgba(0,245,255,0.07),transparent 70%);}
        .card{max-width:460px;width:100%;background:var(--card);border-radius:28px;padding:40px 30px;box-shadow:var(--glow),0 20px 40px rgba(0,0,0,0.3);border:1px solid var(--border);position:relative;overflow:hidden;}
        .card::before{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(0,245,255,0.1),rgba(255,0,170,0.1));opacity:0.5;}
        h1{font-family:'Space Grotesk',sans-serif;font-size:3.2em;text-align:center;margin-bottom:8px;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:float 4s ease-in-out infinite;}
        @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
        p.subtitle{text-align:center;color:#999;font-size:1.1em;margin-bottom:30px;}
        .theme{position:absolute;top:20px;right:20px;font-size:2em;cursor:pointer;z-index:10;}
        .tabs{display:flex;gap:12px;margin-bottom:30px;}
        .tab{flex:1;padding:16px;text-align:center;background:rgba(255,255,255,0.05);border:2px solid var(--border);border-radius:16px;cursor:pointer;transition:all .3s;font-weight:600;}
        .tab.active{background:var(--accent);color:#000;border-color:var(--accent);box-shadow:var(--glow);}
        input{width:100%;padding:18px 20px;background:rgba(255,255,255,0.07);border:2px solid var(--border);border-radius:18px;color:var(--text);font-size:1.1em;margin-bottom:20px;transition:all .3s;}
        input:focus{outline:none;border-color:var(--accent);box-shadow:var(--glow);}
        button{width:100%;padding:20px;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border:none;border-radius:18px;font-size:1.3em;font-weight:700;cursor:pointer;transition:all .3s;box-shadow:var(--glow);}
        button:hover{transform:translateY(-4px);box-shadow:0 20px 40px rgba(0,245,255,0.4);}
        #status{margin-top:25px;padding:16px;border-radius:16px;text-align:center;font-weight:600;font-size:1.1em;min-height:60px;display:flex;align-items:center;justify-content:center;gap:10px;}
        .spinner{width:22px;height:22px;border:3px solid rgba(0,245,255,0.3);border-top-color:var(--accent);border-radius:50%;animation:spin 1s linear infinite;}
        @keyframes spin{to{transform:rotate(360deg)}}
        @media(max-width:480px){h1{font-size:2.6em;}.card{padding:30px 20px;}}
    </style>
</head>
<body>
    <div class="theme" onclick="document.body.dataset.theme=document.body.dataset.theme==='light'?'':'light'">☀️</div>
    <div class="card">
        <h1>AxtarGet</h1>
        <p class="subtitle">Filigransız • 720p • 5 saniyəyə</p>
        <div class="tabs">
            <div class="tab active" onclick="setType('video')">Video</div>
            <div class="tab" onclick="setType('music')">Musiqi</div>
        </div>
        <input type="text" id="url" placeholder="TikTok, Instagram, YouTube linki...">
        <button onclick="download()">ENDİR</button>
        <div id="status"></div>
    </div>

    <script>
        let type='video';
        function setType(t){type=t;document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));event.target.classList.add('active');}
        function status(msg,spin=false){const s=document.getElementById('status');s.innerHTML=spin?'<div class="spinner"></div>'+msg:msg;}
        async function download(){
            const url=document.getElementById('url').value.trim();
            if(!url)return status('Link daxil et!');
            status('Endirilir... 5-10 saniyə',true);
            const r=await fetch("/download",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url,type})});
            if(r.ok){
                const blob=await r.blob();
                const a=document.createElement('a');
                a.href=URL.createObjectURL(blob);
                a.download=type==='music'?'music.mp3':'video.mp4';
                a.click();
                status('✅ Uğurla endirildi! Növbətini göndər');
                document.getElementById('url').value='';
            }else status('Xəta oldu, linki yoxla');
        }
        document.getElementById('url').addEventListener('keypress',e=>e.key==='Enter'&&download());
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
        'concurrent_fragment_downloads': 10,
        'outtmpl': 'file.%(ext)s',
        'format': 'best[height<=720]/best' if t == "video" else 'bestaudio/best',
    }
    if t == "music":
        opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if t == "music":
                filename = filename.rsplit('.', 1)[0] + '.mp3'
        return send_file(filename, as_attachment=True, download_name="video.mp4" if t == "video" else "music.mp3")
    except Exception as e:
        print(e)
        return "Xəta", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
