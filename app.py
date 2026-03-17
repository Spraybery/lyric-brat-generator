import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from whisper_extract import transcribe_to_json

app = Flask(__name__)

TEMP_DIR = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Extension-based allowlist
ALLOWED_EXTENSIONS = {"mp4", "mp3", "wav", "m4a", "mov", "webm", "ogg", "flac", "aac", "wma", "opus"}

# MIME-type prefixes that are always accepted regardless of extension
ALLOWED_MIME_PREFIXES = ("audio/", "video/")

# MIME type → fallback extension when filename has none
MIME_TO_EXT = {
    "audio/mpeg":  "mp3",
    "audio/mp4":   "m4a",
    "audio/wav":   "wav",
    "audio/ogg":   "ogg",
    "audio/flac":  "flac",
    "audio/aac":   "aac",
    "audio/webm":  "webm",
    "video/mp4":   "mp4",
    "video/webm":  "webm",
    "video/quicktime": "mov",
}


def resolve_extension(filename, mime_type):
    """Return the file extension to use, falling back to MIME type if needed."""
    safe = secure_filename(filename)
    if "." in safe:
        return safe.rsplit(".", 1)[1].lower()
    # No extension — derive from MIME type
    base_mime = mime_type.split(";")[0].strip().lower()
    return MIME_TO_EXT.get(base_mime, "tmp")


def is_allowed(filename, mime_type):
    safe = secure_filename(filename)
    if "." in safe and safe.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS:
        return True
    base_mime = (mime_type or "").split(";")[0].strip().lower()
    return any(base_mime.startswith(p) for p in ALLOWED_MIME_PREFIXES)


@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["video"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    mime_type = file.content_type or ""

    if not is_allowed(file.filename, mime_type):
        return jsonify({"error": f"Unsupported file type: {file.filename} ({mime_type})"}), 400

    ext = resolve_extension(file.filename, mime_type)
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(TEMP_DIR, unique_name)
    file.save(filepath)

    try:
        model = request.form.get("model", "base")
        result = transcribe_to_json(filepath, model_name=model)
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
