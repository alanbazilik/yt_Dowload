from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import uuid
import threading
import time

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🧹 Limpador automático (remove arquivos antigos)
def cleanup_files():
    while True:
        now = time.time()
        for f in os.listdir(DOWNLOAD_FOLDER):
            path = os.path.join(DOWNLOAD_FOLDER, f)
            if os.path.isfile(path):
                if now - os.path.getmtime(path) > 3600:  # 1 hora
                    os.remove(path)
        time.sleep(600)  # limpa a cada 10 min

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

        # Configurações do yt-dlp
        ydl_opts = {
            "format": "bestaudio/best" if type_ == "mp3" else "bestvideo+bestaudio",
            "outtmpl": filepath + ".%(ext)s",

            # evita erro de "JavaScript runtime" no YouTube
            "extractor_args": {
                "youtube": {
                    "player_client": ["default"]
                }
            }
        }

        if type_ == "mp3":
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320"
            }]

        # Baixa o vídeo
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        # Determina a extensão final
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
