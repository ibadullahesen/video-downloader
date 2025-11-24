from flask import Flask, request, render_template_string, send_file
import yt_dlp
import os

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="az" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AxtarGet – Video & Musiqi Endirici</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        body { background: linear-gradient(135deg, #0f0229 0%, #1a0033 50%, #0f0229 100%); }
        .blob { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.3; animation: float 20s infinite; }
        .blob1 { width: 500px; height: 500px; background: #8b5cf6; top: -10%; left: -10%; animation-delay: 0s; }
        .blob2 { width: 400px; height: 400px; background: #06b6d4; bottom: -10%; right: -10%; animation-delay: 7s; }
        .blob3 { width: 300px; height: 300px; background: #ec4899; top: 50%; left: 50%; animation-delay: 14s; }
        @keyframes float { 0%,100% { transform: translate(0,0) rotate(0deg); } 50% { transform: translate(100px, -100px) rotate(180deg); } }
    </style>
</head>
<body class="min-h-screen relative overflow-hidden text-white">
    <div class="blob blob1"></div>
    <div class="blob blob2"></div>
    <div class="blob blob3"></div>

    <div class="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div class="w-full max-w-2xl">
            <div class="text-center mb-10">
                <div class="flex justify-center items-center gap-4 mb-4">
                    <div class="p-4 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-2xl shadow-2xl">
                        <i data-lucide="download" class="w-10 h-10 text-white"></i>
                    </div>
                    <h1 class="text-6xl font-black bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                        AxtarGet
                    </h1>
                </div>
                <p class="text-gray-300 text-lg">TikTok • Instagram – Filigransız və Sürətli</p>
            </div>

            <div class="bg-white/5 backdrop-blur-2xl rounded-3xl p-8 border border-white/10 shadow-2xl">
                <div class="flex gap-4 mb-8">
                    <button onclick="setType('video')" id="tab-video" class="flex-1 py-4 rounded-2xl font-bold text-lg transition-all duration-300 flex items-center justify-center gap-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/50">
                        <i data-lucide="video" class="w-6 h-6"></i> Video
                    </button>
                    <button onclick="setType('music')" id="tab-music" class="flex-1 py-4 rounded-2xl font-bold text-lg transition-all duration-300 flex items-center justify-center gap-3 bg-white/10 text-gray-300 hover:bg-white/20">
                        <i data-lucide="music" class="w-6 h-6"></i> Musiqi
                    </button>
                </div>

                <input type="text" id="url" oninput="checkUrl()" placeholder="TikTok və ya Instagram linki yapışdır..." class="w-full px-6 py-5 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/30 transition-all text-lg mb-6">

                <button onclick="download()" class="w-full py-5 bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 text-white font-black text-xl rounded-2xl hover:shadow-2xl hover:shadow-purple-500/50 transition-all duration-300 flex items-center justify-center gap-3">
                    <i data-lucide="download" class="w-7 h-7" id="icon"></i>
                    <span id="text">ENDİR</span>
                </button>

                <div id="status" class="mt-6 text-center font-semibold text-lg"></div>

                <div id="youtube-block" class="hidden mt-6 p-5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl text-center font-bold text-white shadow-lg">
                    YouTube hazırda yenilənmə işlərindədir<br>
                    Tezliklə ən sürətli şəkildə geri qayıdacaq!
                </div>

                <div class="mt-10 grid grid-cols-3 gap-4 text-center">
                    <div class="bg-white/5 rounded-2xl py-4"><div class="text-3xl font-black text-cyan-400">720p</div><div class="text-sm text-gray-400">Keyfiyyət</div></div>
                    <div class="bg-white/5 rounded-2xl py-4"><div class="text-3xl font-black text-purple-400">5-8 sn</div><div class="text-sm text-gray-400">Sürət</div></div>
                    <div class="bg-white/5 rounded-2xl py-4"><div class="text-3xl font-black text-pink-400">Təmiz</div><div class="text-sm text-gray-400">Filigransız</div></div>
                </div>
            </div>
            <p class="text-center text-gray-500 text-sm mt-8">© 2025 AxtarGet – Azərbaycanın ən sürətlisi</p>
        </div>
    </div>

    <script>
        lucide.createIcons();
        let type = 'video';
        const youtubeRegex = /(youtube\.com|youtu\.be)/i;

        function checkUrl() {
            const url = document.getElementById('url').value.trim();
            const block = document.getElementById('youtube-block');
            if (youtubeRegex.test(url)) {
                block.classList.remove('hidden');
                document.getElementById('status').textContent = '';
            } else {
                block.classList.add('hidden');
            }
        }

        function setType(t) {
            type = t;
            document.getElementById('tab-video').className = t==='video' ? 'flex-1 py-4 rounded-2xl font-bold text-lg transition-all duration-300 flex items-center justify-center gap-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/50' : 'flex-1 py-4 rounded-2xl font-bold text-lg transition-all duration-300 flex items-center justify-center gap-3 bg-white/10 text-gray-300 hover:bg-white/20';
            document.getElementById('tab-music').className = t==='music' ? 'flex-1 py-4 rounded-2xl font-bold text-lg transition-all duration-300 flex items-center justify-center gap-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg shadow-purple-500/50' : 'flex-1 py-4 rounded-2xl font-bold text-lg transition-all duration-300 flex items-center justify-center gap-3 bg-white/10 text-gray-300 hover:bg-white/20';
        }

        async function download() {
            const url = document.getElementById('url').value.trim();
            if (!url) return status('Link daxil et!', 'text-red-400');
            if (youtubeRegex.test(url)) return status('YouTube tezliklə geri qayıdacaq!', 'text-yellow-400');

            document.getElementById('text').textContent = 'Endirilir...';
            document.getElementById('icon').setAttribute('data-lucide', 'loader-2');
            lucide.createIcons();
            document.getElementById('icon').classList.add('animate-spin');

            try {
                const r = await fetch("/download", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url,type})});
                if (r.ok) {
                    const blob = await r.blob();
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = type==='music'?'music.mp3':'video.mp4';
                    a.click();
                    status('Uğurla endirildi! Növbətini göndər', 'text-green-400');
                    document.getElementById('url').value = '';
                } else status('Xəta oldu. Linki yoxla', 'text-red-400');
            } catch { status('Bağlantı xətası', 'text-red-400'); }
            finally {
                document.getElementById('text').textContent = 'ENDİR';
                document.getElementById('icon').setAttribute('data-lucide', 'download');
                document.getElementById('icon').classList.remove('animate-spin');
                lucide.createIcons();
            }
        }

        function status(msg, cls) {
            const s = document.getElementById('status');
            s.textContent = msg;
            s.className = 'mt-6 text-center font-bold text-lg ' + cls;
        }

        document.getElementById('url').addEventListener('keypress', e => e.key==='Enter' && download());
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

    # YouTube blok
    if "youtube.com" in url or "youtu.be" in url:
        return "YouTube tezliklə geri qayıdacaq!", 400

    # Ən sürətli ayarlar
    opts = {
        'quiet': True,
        'no_warnings': True,
        'concurrent_fragment_downloads': 20,  # 20 parça eyni anda → çox sürətli
        'outtmpl': 'file.%(ext)s',
        'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/best' if t == "video" else 'bestaudio/best',
        'retries': 5,
        'fragment_retries': 10,
    }

    if t == "music":
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',  # 320 əvəzinə 192 → daha sürətli
        }]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if t == "music":
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        return send_file(filename, as_attachment=True, download_name="video.mp4" if t == "video" else "music.mp3")
    except Exception as e:
        print("XƏTA:", e)
        return "Xəta oldu. Linki yoxla", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
