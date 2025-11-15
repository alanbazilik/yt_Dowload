from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid
import threading
import time

# ⛔ Corrige erro "ffmpeg not found" no Replit
os.environ["PATH"] += os.pathsep + "/usr/bin"

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🧹 Limpador automático
def cleanup_files():
    while True:
        now = time.time()
        for f in os.listdir(DOWNLOAD_FOLDER):
            path = os.path.join(DOWNLOAD_FOLDER, f)
            if os.path.isfile(path) and now - os.path.getmtime(path) > 3600:
                os.remove(path)
        time.sleep(300)

threading.Thread(target=cleanup_files, daemon=True).start()


@app.route("/")
def home():
    return {"status": "online", "message": "API FLASK YT-DLP OK"}, 200


@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.json
        url = data.get("url")
        type_ = data.get("type", "mp3")

        if not url:
            return jsonify({"error": "URL não fornecida"}), 400

        temp_id = str(uuid.uuid4())
        filepath = os.path.join(DOWNLOAD_FOLDER, temp_id)

        # ⚡ Evita erro quando cookies.txt não existe
        cookie_file = "cookies.txt" if os.path.exists("cookies.txt") else None

        # ⚡ Configurações recomendadas para REPLIT
        ydl_opts = {
            "cookiefile": cookie_file,
            "format": "bestaudio/best" if type_ == "mp3" else "bestvideo[height<=720]+bestaudio/best",
            "outtmpl": filepath + ".%(ext)s",
            "noplaylist": True,
            "geo_bypass": True,
            "user_agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
        }

        if type_ == "mp3":
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"   # 320 falha no Replit → usar 192
            }]

        # 🔥 Faz o download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # 🔧 Arquivo final gerado
        if type_ == "mp3":
            final_file = filepath + ".mp3"
        else:
            ext = info.get("ext", "mp4")
            final_file = f"{filepath}.{ext}"

        return send_file(final_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔥 Replit usa porta dinâmica
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
