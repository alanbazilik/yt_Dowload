from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid
import threading
import time

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🧹 Limpador automático: remove arquivos após 1h
def cleanup_files():
    while True:
        now = time.time()
        for f in os.listdir(DOWNLOAD_FOLDER):
            path = os.path.join(DOWNLOAD_FOLDER, f)
            if os.path.isfile(path) and now - os.path.getmtime(path) > 3600:
                os.remove(path)
        time.sleep(600)

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

        # ⚡ Configurações yt-dlp ANTI-BOT + COOKIES
        ydl_opts = {
            "cookiefile": "cookies.txt",    # ← cookies reais aqui
            "format": "bestaudio/best" if type_ == "mp3" else "bestvideo+bestaudio",
            "outtmpl": filepath + ".%(ext)s",

            # 🧩 ESSA PARTE É O BYPASS IMPORTANTE
            "extractor_args": {
                "youtube": {
                    "player_client": ["web", "android", "default"],
                    "player_skip": ["webpage", "configs"],
                    "visitor_data": ["CgtiZUZlZ1ZUR0V9dQ=="]  
                },
                "youtubetab": {
                    "skip": ["webpage"]
                }
            },

            # Ajuda a evitar bloqueios
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
                "preferredquality": "320"
            }]

        # 🔥 Baixar
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # 🔧 Determina o arquivo final
        if type_ == "mp3":
            final_file = filepath + ".mp3"
        else:
            ext = info.get("ext", "mp4")
            final_file = f"{filepath}.{ext}"

        return send_file(final_file, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
