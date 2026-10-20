"""Model Training Script for Gujarati-English Code-Mixed Text Understanding.

Loads CSV datasets:
- backend/data/sentiment_dataset.csv
- backend/data/topic_dataset.csv

Trains TF-IDF vectorizers and Logistic Regression classifiers for:
1. Sentiment Classification (Positive, Negative, Neutral)
2. Topic Classification (Education, Sports, Technology, Entertainment, Food, Travel, Shopping, General)

Evaluates on test splits:
- Accuracy
- Precision (weighted)
- Recall (weighted)
- F1-score (weighted)
- Confusion Matrix

Saves models and metrics to backend/models/:
- sentiment_vectorizer.pkl
- sentiment_model.pkl
- topic_vectorizer.pkl
- topic_model.pkl
- metrics.json
"""

import csv
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
from nlp.normalizer import normalize_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")


def load_dataset(csv_path: str, text_col: str = "text", label_col: str = "label") -> tuple:
    """Load text and labels from CSV file."""
    texts = []
    labels = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_text = row[text_col].strip()
            label = row[label_col].strip()
            if raw_text and label:
                # Apply informal normalization
                cleaned_text = normalize_text(raw_text)
                texts.append(cleaned_text)
                labels.append(label)
    return texts, labels


def train_and_evaluate(
    name: str,
    texts: list,
    labels: list,
    vec_filename: str,
    model_filename: str
) -> dict:
    """Train TF-IDF + LogisticRegression model, evaluate, and save artifacts."""
    print(f"\n==========================================")
    print(f" Training {name} Classifier")
    print(f" Total Samples: {len(texts)} | Unique Classes: {len(set(labels))}")
    print(f"==========================================")

    # Train/Test Split (80% train, 20% test with stratification)
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # TF-IDF Feature Extraction
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Logistic Regression Classifier
    model = LogisticRegression(
        C=1.0,
        max_iter=1000,
        random_state=42
    )
    model.fit(X_train_vec, y_train)

    # Evaluation on Test Split
    y_pred = model.predict(X_test_vec)

    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_test, y_pred, average="weighted", zero_division=0
    )
    cm = confusion_matrix(y_test, y_pred, labels=model.classes_)

    print(f"\n--- {name} Evaluation Metrics ---")
    print(f"Accuracy : {acc:.4f} ({acc * 100:.2f}%)")
    print(f"Precision: {prec:.4f} ({prec * 100:.2f}%)")
    print(f"Recall   : {rec:.4f} ({rec * 100:.2f}%)")
    print(f"F1-Score : {f1:.4f} ({f1 * 100:.2f}%)")
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred, zero_division=0))
    print(f"Confusion Matrix (Classes: {list(model.classes_)}):\n{cm}\n")

    # Save artifacts
    os.makedirs(MODELS_DIR, exist_ok=True)
    vec_path = os.path.join(MODELS_DIR, vec_filename)
    model_path = os.path.join(MODELS_DIR, model_filename)

    joblib.dump(vectorizer, vec_path)
    joblib.dump(model, model_path)
    print(f"Saved vectorizer -> {vec_path}")
    print(f"Saved model      -> {model_path}")

    return {
        "accuracy": round(float(acc) * 100, 2),
        "precision": round(float(prec) * 100, 2),
        "recall": round(float(rec) * 100, 2),
        "f1_score": round(float(f1) * 100, 2),
        "classes": list(model.classes_),
        "sample_count": len(texts)
    }


def main():
    sentiment_csv = os.path.join(DATA_DIR, "sentiment_dataset.csv")
    topic_csv = os.path.join(DATA_DIR, "topic_dataset.csv")

    if not os.path.exists(sentiment_csv):
        print(f"Error: {sentiment_csv} not found.")
        sys.exit(1)

    if not os.path.exists(topic_csv):
        print(f"Error: {topic_csv} not found.")
        sys.exit(1)

    # 1. Train Sentiment Model
    sent_texts, sent_labels = load_dataset(sentiment_csv, text_col="text", label_col="sentiment")
    sentiment_metrics = train_and_evaluate(
        name="Sentiment",
        texts=sent_texts,
        labels=sent_labels,
        vec_filename="sentiment_vectorizer.pkl",
        model_filename="sentiment_model.pkl"
    )

    # 2. Train Topic Model
    topic_texts, topic_labels = load_dataset(topic_csv, text_col="text", label_col="topic")
    topic_metrics = train_and_evaluate(
        name="Topic",
        texts=topic_texts,
        labels=topic_labels,
        vec_filename="topic_vectorizer.pkl",
        model_filename="topic_model.pkl"
    )

    # 3. Save evaluation metrics to JSON for frontend/API reporting
    all_metrics = {
        "sentiment": sentiment_metrics,
        "topic": topic_metrics
    }
    metrics_path = os.path.join(MODELS_DIR, "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, indent=4)
    print(f"\nAll metrics saved to -> {metrics_path}")
    print("\nTraining completed successfully!")


if __name__ == "__main__":
    main()
