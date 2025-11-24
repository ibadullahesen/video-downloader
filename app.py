from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os

app = Flask(__name__)

HTML = '''[SƏNİN SON GÖZƏL HTML KODUN – dəyişdirmə, olduğu kimi qalsın]'''

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
        'format': 'best[height<=720]/best' if t == "video" else 'bestaudio/best',  # 720p → daha sürətli
        'concurrent_fragment_downloads': 10,  # 10 parça eyni anda endirir
        'outtmpl': 'file.%(ext)s',
    }

    if t == "music":
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if t == "music":
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        return send_file(
            filename,
            as_attachment=True,
            download_name="video.mp4" if t == "video" else "music.mp3"
        )
    except Exception as e:
        print("Xəta:", e)
        return "Link xətası", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
