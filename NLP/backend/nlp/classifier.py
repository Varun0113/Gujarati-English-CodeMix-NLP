"""Classifier Module for Sentiment and Topic Classification.

Loads TF-IDF vectorizers and Logistic Regression models trained on
Gujarati-English code-mixed text to predict:
- Sentiment (Positive, Negative, Neutral) + complete probability distribution
- Topic (8 domains) + complete probability distribution
"""

import json
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

import joblib

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

# Cached model instances
_sentiment_vectorizer = None
_sentiment_model = None
_topic_vectorizer = None
_topic_model = None
_metrics_cache = None


def load_models():
    """Load serialized model artifacts from the models directory."""
    global _sentiment_vectorizer, _sentiment_model, _topic_vectorizer, _topic_model

    sentiment_vec_path = os.path.join(MODELS_DIR, "sentiment_vectorizer.pkl")
    sentiment_model_path = os.path.join(MODELS_DIR, "sentiment_model.pkl")
    topic_vec_path = os.path.join(MODELS_DIR, "topic_vectorizer.pkl")
    topic_model_path = os.path.join(MODELS_DIR, "topic_model.pkl")

    if not (os.path.exists(sentiment_vec_path) and os.path.exists(sentiment_model_path)):
        raise FileNotFoundError(
            f"Sentiment model files not found in {MODELS_DIR}. Run train_models.py first."
        )

    if not (os.path.exists(topic_vec_path) and os.path.exists(topic_model_path)):
        raise FileNotFoundError(
            f"Topic model files not found in {MODELS_DIR}. Run train_models.py first."
        )

    _sentiment_vectorizer = joblib.load(sentiment_vec_path)
    _sentiment_model = joblib.load(sentiment_model_path)
    _topic_vectorizer = joblib.load(topic_vec_path)
    _topic_model = joblib.load(topic_model_path)


def get_model_metrics() -> dict:
    """Retrieve actual evaluation metrics saved during training."""
    global _metrics_cache
    if _metrics_cache is not None:
        return _metrics_cache

    metrics_path = os.path.join(MODELS_DIR, "metrics.json")
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, "r", encoding="utf-8") as f:
                _metrics_cache = json.load(f)
                return _metrics_cache
        except Exception:
            pass
    return {}


def predict_sentiment_full(normalized_text: str) -> dict:
    """Predict sentiment class, confidence, and complete probability distribution.

    Returns:
        dict: {
            "label": str,
            "confidence": float,
            "probabilities": {class_name: probability_pct}
        }
    """
    global _sentiment_vectorizer, _sentiment_model
    if _sentiment_model is None or _sentiment_vectorizer is None:
        load_models()

    if not normalized_text or not normalized_text.strip():
        classes = list(_sentiment_model.classes_) if _sentiment_model else ["Negative", "Neutral", "Positive"]
        default_prob = round(100.0 / len(classes), 1)
        return {
            "label": "Neutral",
            "confidence": 0.0,
            "probabilities": {c: default_prob for c in classes}
        }

    features = _sentiment_vectorizer.transform([normalized_text])
    probabilities = _sentiment_model.predict_proba(features)[0]
    classes = _sentiment_model.classes_
    best_idx = probabilities.argmax()

    # Build sorted probability dictionary (descending)
    prob_pairs = sorted(
        zip(classes, probabilities),
        key=lambda x: x[1],
        reverse=True
    )
    prob_dict = {str(c): round(float(p) * 100.0, 1) for c, p in prob_pairs}

    sentiment_label = str(classes[best_idx])
    confidence = round(float(probabilities[best_idx]) * 100.0, 1)

    return {
        "label": sentiment_label,
        "confidence": confidence,
        "probabilities": prob_dict
    }


def predict_sentiment(normalized_text: str) -> tuple:
    """Legacy helper returning (label, confidence)."""
    res = predict_sentiment_full(normalized_text)
    return res["label"], res["confidence"]


def predict_topic_full(normalized_text: str) -> dict:
    """Predict topic class, confidence, and complete probability distribution.

    Returns:
        dict: {
            "label": str,
            "confidence": float,
            "probabilities": {class_name: probability_pct}
        }
    """
    global _topic_vectorizer, _topic_model
    if _topic_model is None or _topic_vectorizer is None:
        load_models()

    if not normalized_text or not normalized_text.strip():
        classes = list(_topic_model.classes_) if _topic_model else ["General"]
        default_prob = round(100.0 / len(classes), 1)
        return {
            "label": "General",
            "confidence": 0.0,
            "probabilities": {c: default_prob for c in classes}
        }

    features = _topic_vectorizer.transform([normalized_text])
    probabilities = _topic_model.predict_proba(features)[0]
    classes = _topic_model.classes_
    best_idx = probabilities.argmax()

    # Build sorted probability dictionary (descending)
    prob_pairs = sorted(
        zip(classes, probabilities),
        key=lambda x: x[1],
        reverse=True
    )
    prob_dict = {str(c): round(float(p) * 100.0, 1) for c, p in prob_pairs}

    topic_label = str(classes[best_idx])
    confidence = round(float(probabilities[best_idx]) * 100.0, 1)

    return {
        "label": topic_label,
        "confidence": confidence,
        "probabilities": prob_dict
    }


def predict_topic(normalized_text: str) -> tuple:
    """Legacy helper returning (label, confidence)."""
    res = predict_topic_full(normalized_text)
    return res["label"], res["confidence"]
