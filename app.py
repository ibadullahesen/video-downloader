from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="az">
<head>
    <meta charset="UTF-8">
    <title>Filigransız Video Endirici</title>
    <style>body {font-family: Arial; text-align: center; padding: 50px; background: #f4f4f4;}
    input {width: 70%; padding: 10px; margin: 10px;}
    button {padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer;}
    #result {margin: 20px;}</style>
</head>
<body>
    <h1>🚀 Filigransız Video Yüklə (TikTok, Instagram, YouTube)</h1>
    <input type="text" id="url" placeholder="Linki buraya yapışdır...">
    <button onclick="download()">Endir</button>
    <a id="result" style="display:none;">Video endirilir...</a>

    <script>
    async function download() {
        const url = document.getElementById("url").value;
        if (!url) return alert("Link daxil et!");
        document.getElementById("result").style.display = "block";
        document.getElementById("result").textContent = "Endirilir...";
        const res = await fetch("/download", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({url: url})
        });
        if (res.ok) {
            const blob = await res.blob();
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "video.mp4";
            link.click();
            document.getElementById("result").textContent = "Hazır! Endirildi.";
        } else {
            document.getElementById("result").textContent = "Xəta: Linki yoxla.";
        }
    }
    </script>
</body>
</html>
'''

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return "Xəta: Link yoxdur", 400

    ydl_opts = {
        'format': 'best[height<=1080]/best',  # 1080p və ya ən yaxşısı
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return send_file(filename, as_attachment=True, download_name="video.mp4")
    except Exception as e:
        return f"Xəta: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
