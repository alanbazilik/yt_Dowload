from flask import Flask, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 🔥 ROTA OBRIGATÓRIA PARA KOYEB (health check e scale-to-zero)
@app.route("/")
def home():
    return {"status": "running"}, 200


@app.route("/download", methods=["POST"])
def download():
    data = request.json
    url = data.get("url")
    type_ = data.get("type", "mp3")  # mp3 ou mp4
    
    if not url:
        return {"error": "URL não fornecida"}, 400

    filename = f"{uuid.uuid4()}.{type_}"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    
    ydl_opts = {
        'format': 'bestaudio/best' if type_ == 'mp3' else 'bestvideo+bestaudio',
        'outtmpl': filepath,
    }

    if type_ == 'mp3':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    # 🔥 KOYEB USA A PORTA DEFINIDA EM $PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
