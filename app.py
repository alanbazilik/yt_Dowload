from flask import Flask, request, send_file
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return {"status": "running"}, 200


@app.route("/download", methods=["POST"])
def download():
    data = request.json
    url = data.get("url")
    type_ = data.get("type", "mp3")

    if not url:
        return {"error": "URL não fornecida"}, 400

    temp_id = str(uuid.uuid4())
    filename = f"{temp_id}.{type_}"
    filepath = os.path.join(DOWNLOAD_FOLDER, temp_id)

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

    final_file = filepath if type_ == "mp4" else filepath + ".mp3"

    return send_file(final_file, as_attachment=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
