"""Flask Application for Gujarati-English Code-Mixed Text Understanding System.

Provides standalone web application and REST API endpoints:
- GET  /           : Serves the web application (or health JSON if Accept: application/json)
- GET  /health     : Health status JSON
- GET  /metrics    : Evaluated machine learning model metrics
- POST /analyze    : Full NLP analysis pipeline on input text
- GET  /favicon.ico: Lightweight favicon handler (prevents 404 console errors)
"""

import os
import sys

# Ensure Windows C-extension DLLs (MKL/OpenMP) can be resolved if using Anaconda
if sys.platform == "win32":
    anaconda_bin = os.path.join(sys.prefix, "Library", "bin")
    if os.path.exists(anaconda_bin) and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(anaconda_bin)
        except Exception:
            pass

from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

from nlp.classifier import get_model_metrics
from nlp.pipeline import analyze_text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)
CORS(app)


@app.route("/", methods=["GET"])
def index():
    """Serve the standalone frontend application."""
    accept = request.headers.get("Accept", "")
    # If client explicitly requests JSON only (e.g. CLI or health check script)
    if "application/json" in accept and "text/html" not in accept:
        return jsonify({
            "status": "ok",
            "message": "Gujarati-English NLP backend is running"
        })

    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return send_from_directory(FRONTEND_DIR, "index.html")

    return jsonify({
        "status": "ok",
        "message": "Gujarati-English NLP backend is running"
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "Gujarati-English NLP backend is running"
    })


@app.route("/metrics", methods=["GET"])
def metrics():
    """Return trained model evaluation metrics."""
    data = get_model_metrics()
    return jsonify({
        "success": True,
        "metrics": data
    })


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze code-mixed Gujarati-English text through the NLP pipeline.

    Expected JSON body:
        {"text": "Aaje college ma bau boring lecture hato"}
    """
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request body must be valid JSON."
        }), 400

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({
            "success": False,
            "error": "Invalid JSON format."
        }), 400

    text = payload.get("text")
    if text is None:
        return jsonify({
            "success": False,
            "error": "Missing 'text' field in request body."
        }), 400

    if not isinstance(text, str):
        return jsonify({
            "success": False,
            "error": "'text' field must be a string."
        }), 400

    text_clean = text.strip()
    if not text_clean:
        return jsonify({
            "success": False,
            "error": "Please enter some text to analyze."
        }), 400

    if len(text_clean) > 500:
        return jsonify({
            "success": False,
            "error": "Input text exceeds maximum allowed length of 500 characters."
        }), 400

    try:
        result = analyze_text(text_clean)
        return jsonify({
            "success": True,
            "result": result
        }), 200
    except FileNotFoundError:
        return jsonify({
            "success": False,
            "error": "Model files not found. Please train models first."
        }), 500
    except Exception:
        # Avoid exposing raw Python stack traces to the frontend
        return jsonify({
            "success": False,
            "error": "The NLP service could not process this request. Please try again."
        }), 500


@app.route("/favicon.ico", methods=["GET"])
def favicon():
    """Lightweight SVG favicon to prevent 404 console errors in browsers."""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<rect width="100" height="100" rx="20" fill="#4F46E5"/>'
        '<text x="50%" y="42%" font-family="system-ui, sans-serif" font-size="30" '
        'font-weight="bold" fill="#ffffff" text-anchor="middle" dominant-baseline="middle">ગુ</text>'
        '<text x="50%" y="74%" font-family="system-ui, sans-serif" font-size="26" '
        'font-weight="bold" fill="#A5B4FC" text-anchor="middle" dominant-baseline="middle">EN</text>'
        '</svg>'
    )
    return Response(svg, mimetype="image/svg+xml")


# Static assets serving for convenience when running via Flask
@app.route("/css/<path:filename>")
def serve_css(filename):
    css_dir = os.path.join(FRONTEND_DIR, "css")
    return send_from_directory(css_dir, filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    js_dir = os.path.join(FRONTEND_DIR, "js")
    return send_from_directory(js_dir, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
