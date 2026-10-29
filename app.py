from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
import cv2, os, json, uuid
from werkzeug.utils import secure_filename

ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(ROOT, "uploads")
RESULT_DIR = os.path.join(ROOT, "results")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024
ALLOWED = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
models = {}

@app.get("/")
def home():
    return send_from_directory(ROOT, "index.html")

@app.get("/<path:filename>")
def static_files(filename):
    if filename in {"style.css", "script.js"}:
        return send_from_directory(ROOT, filename)
    return ("Not found", 404)

@app.post("/api/detect")
def detect():
    uploaded = request.files.get("video")
    if not uploaded or not uploaded.filename:
        return jsonify(error="Choose a video first."), 400
    ext = os.path.splitext(secure_filename(uploaded.filename))[1].lower()
    if ext not in ALLOWED:
        return jsonify(error="Unsupported video format."), 400
    model_name = request.form.get("model", "yolov8n.pt")
    if model_name not in {"yolov8n.pt", "yolov8s.pt", "yolov8m.pt"}:
        return jsonify(error="Invalid model selection."), 400
    try:
        confidence = max(0.1, min(0.9, float(request.form.get("confidence", "35")) / 100))
        requested_classes = json.loads(request.form.get("classes", "[]"))
        input_name = uuid.uuid4().hex + ext
        input_path = os.path.join(UPLOAD_DIR, input_name)
        uploaded.save(input_path)
        output_name = "detected_" + uuid.uuid4().hex + ".mp4"
        output_path = os.path.join(RESULT_DIR, output_name)
        if model_name not in models:
            models[model_name] = YOLO(model_name)
        model = models[model_name]
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return jsonify(error="Could not read the uploaded video."), 400
        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width <= 0 or height <= 0:
            cap.release()
            return jsonify(error="Video dimensions could not be read."), 400
        writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
        # COCO class IDs for the selected common labels
        class_ids_by_name = {"person":0,"bicycle":1,"car":2,"motorcycle":3,"bus":5,"truck":7,"cat":15,"dog":16}
        ids = [class_ids_by_name[c] for c in requested_classes if c in class_ids_by_name]
        while True:
            ok, frame = cap.read()
            if not ok: break
            kwargs = {"conf": confidence, "verbose": False}
            if ids: kwargs["classes"] = ids
            result = model.predict(frame, **kwargs)[0]
            writer.write(result.plot())
        cap.release(); writer.release()
        try: os.remove(input_path)
        except OSError: pass
        return jsonify(message="Object detection completed successfully.", video_url="/results/" + output_name)
    except Exception as exc:
        return jsonify(error=str(exc)), 500

@app.get("/results/<path:filename>")
def result_file(filename):
    return send_from_directory(RESULT_DIR, filename, as_attachment=False)

if __name__ == "__main__":
    print("YOLO Vision is running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
