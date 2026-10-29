# YOLO Vision — index.html edition

## What works by opening index.html
- Video selection, drag and drop, and local preview.
- Model, confidence, and common object-class controls.
- Responsive interface.

## Important limitation
A normal static HTML page cannot run the original Python/PyTorch YOLO model by itself. The actual AI video detection feature requires the included Python backend. This package includes both: you can open `index.html` directly for the interface and preview, or run the backend to enable detection.

## Run with AI detection (Windows)
1. Install Python 3.10–3.12 (Python 3.12 is a reasonable choice).
2. Extract this ZIP.
3. Open PowerShell in the extracted folder.
4. Run:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

5. Keep the terminal open and visit `http://127.0.0.1:5000` in Chrome.
6. Upload a video and click **Run object detection**.

The first detection run may download the selected YOLO model and therefore needs an internet connection. Processing time depends on video length and computer hardware.

## Open directly
Double-click `index.html`. Video preview works without the backend. The AI detection button will explain how to start the backend if it is not running.

## Files
- `index.html` — main UI
- `style.css` — page styling
- `script.js` — upload, preview, and backend request logic
- `app.py` — Flask API and YOLO video processing
- `requirements.txt` — Python dependencies
- `uploads/`, `results/` — temporary input/output directories

## Notes
- This starter version detects selected common COCO classes: person, bicycle, car, motorcycle, bus, truck, cat, and dog.
- This is a local development server, not a public production deployment.
- For long or large videos, allow enough RAM, disk space, and processing time.
