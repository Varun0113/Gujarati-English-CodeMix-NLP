# CodeMix Lab — Gujarati–English Code-Mixed Text Understanding System

An academic Natural Language Processing (NLP) standalone research interface for understanding, analyzing, and visualizing Gujarati–English code-mixed text.

---

## Project Overview

In multilingual online communication, users frequently mix languages—combining English terminology with Gujarati written in both native Gujarati script and Romanized phonetic spellings.

**CodeMix Lab** is a self-contained, academic-quality NLP research interface that performs word-level language identification, informal text normalization, Romanized Gujarati variant handling, sentiment classification, and topic classification through an interactive web workspace with research-oriented visualizations.

---

## Problem Statement

Code-mixed Gujarati–English text poses significant challenges for standard Natural Language Processing pipelines:
1. **Script Variation:** Informal text blends native Gujarati script (Unicode `\u0A80`–`\u0AFF`) and Latin-script Romanized Gujarati.
2. **Non-Standard Phonetic Spellings:** Romanized Gujarati lacks official spelling rules (e.g., *che*, *chhe*, *ch*, *cheee* for 'છે'; *mne*, *mane*, *maney* for 'મને').
3. **Lexical Borrowing & Switching:** Intra-sentential code-switching creates complex word-level transitions between English and Gujarati vocabularies.
4. **Context Loss in Small-Scale ML:** Standard bag-of-words pipelines must balance vocabulary sparsity with sublinear n-gram feature representations.

---

## Features

- **Arbitrary Free-Text Analysis:** Accepts any user-entered code-mixed text up to 500 characters with live character counting and `Ctrl + Enter` execution.
- **Word-Level Language Identification:** Classifies every token into English, Gujarati (Unicode script), Romanized Gujarati (Latin alphabet), or Unknown.
- **Informal Text Normalization:** Collapses prolonged character sequences (e.g., `goooood` → `good`, `bahuuu` → `bahu`) and expands abbreviations (e.g., `pls` → `please`).
- **Romanized Gujarati Handling:** Canonicalizes colloquial spelling variations (e.g., `bau` → `bahu`, `che` → `chhe`, `mne` → `mane`) while preserving original tokens.
- **Research Summary Card:** Compact overview of language mix, dominant language, sentiment, topic, token counts, and deterministic research insights.
- **Sentiment Probability Graph:** Visualizes real class probability distributions across Positive, Neutral, and Negative polarity via `predict_proba()`.
- **Topic Probability Graph:** Visualizes model class probabilities across all 8 trained topic domains sorted descending.
- **Language Composition Visualization:** Horizontal bar breakdown of language proportions computed directly from token counts.
- **Code-Mixing & Transition Sequence:** Visual token-by-token code-switching sequence flow (e.g., `EN → RG → EN`) and consecutive transition frequency table.
- **Normalization Comparison Table:** Side-by-side original vs. normalized token comparison with `Tokens Changed: X / Y` and Changed `Yes/No` status.
- **Detailed Token Table:** Complete metadata table (`Token`, `Language`, `Normalized`, `Transliteration`) with category summary counts.
- **Model Performance Comparison Chart:** Native CSS grouped bar chart comparing Accuracy, Precision, Recall, and F1-Score loaded directly from `backend/models/metrics.json`.
- **Unknown Token Analysis:** Explicitly flags unmapped tokens with academic honesty rather than making unreliable guesses.

---

## Technology Stack

- **Backend:** Python 3.12, Flask, Flask-CORS
- **NLP / ML:** scikit-learn, joblib, numpy
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (No React, Vue, Angular, or external JS frameworks)
- **Data & Storage:** Local CSV datasets (`backend/data/`), Serialized `.pkl` models (`backend/models/`)

---

## NLP Pipeline

```text
Input
 ↓
Tokenization
 ↓
Language Detection
 ↓
Normalization
 ↓
Romanized Gujarati Handling
 ↓
TF-IDF
 ↓
Logistic Regression
 ↓
Sentiment + Topic
 ↓
Visualization
```

1. **Input:** Raw code-mixed or monolingual text entered by the user.
2. **Tokenization:** Regex-based tokenizer preserving Gujarati script, Latin characters, and punctuation.
3. **Language Detection:** Word-level categorization across Gujarati script, Romanized Gujarati lexicon, English dictionary, and Unknown.
4. **Normalization:** Repeated character reduction, lowercasing, and informal chat abbreviation expansion.
5. **Romanized Gujarati Handling:** Phonetic and colloquial variant mapping to canonical standardized representations.
6. **TF-IDF:** Sublinear term-frequency inverse-document-frequency extraction with (1, 2) word n-grams.
7. **Logistic Regression:** Supervised classification for polarity and domain with full probability vectors.
8. **Sentiment + Topic:** Winner classes and confidence scores extracted from `predict_proba()`.
9. **Visualization:** Real-time rendering of research summary, horizontal distribution bars, sequence flow, and token analysis table.

---

## Project Structure

```text
gujarati-english-nlp/
├── backend/
│   ├── app.py                     # Flask application & REST endpoints
│   ├── requirements.txt           # Python dependencies
│   ├── train_models.py            # Model training & metrics computation
│   ├── nlp/
│   │   ├── classifier.py          # TF-IDF & Logistic Regression classifiers
│   │   ├── language_detector.py   # Word-level language identification
│   │   ├── normalizer.py          # Informal text normalization
│   │   ├── transliterator.py      # Romanized Gujarati variant handling
│   │   └── pipeline.py            # Orchestrator & statistics calculator
│   ├── models/
│   │   ├── sentiment_vectorizer.pkl
│   │   ├── sentiment_model.pkl
│   │   ├── topic_vectorizer.pkl
│   │   ├── topic_model.pkl
│   │   └── metrics.json           # Actual holdout evaluation metrics
│   └── data/
│       ├── sentiment_dataset.csv  # Sentiment training data (115 samples)
│       └── topic_dataset.csv      # Topic training data (126 samples)
├── frontend/
│   ├── index.html                 # Semantic academic UI
│   ├── css/
│   │   └── style.css              # Custom responsive CSS design system
│   └── js/
│       └── app.js                 # Vanilla JS application & chart renderer
├── README.md                      # Documentation
└── .gitignore
```

---

## How to Run

1. Open a terminal in the project directory.
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Start the Flask application:
   ```bash
   python app.py
   ```

---

## URL

Open your web browser and navigate to:

```text
http://127.0.0.1:5000
```

The Flask backend directly serves the frontend interface, static assets, and REST API from this single endpoint.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the standalone web application (`index.html`) |
| `GET` | `/health` | Health status JSON check |
| `GET` | `/metrics` | Returns evaluation metrics loaded from `metrics.json` |
| `POST` | `/analyze` | Executes the complete NLP research pipeline on JSON payload `{"text": "..."}` |
| `GET` | `/favicon.ico` | Inline SVG favicon to prevent 404 browser console logs |

---

## Model Evaluation

Actual metrics evaluated on stratified 20% holdout test splits (from `backend/models/metrics.json`):

### Sentiment Classifier

| Metric | Score |
|---|---:|
| Accuracy | 69.57% |
| Precision (Weighted) | 77.90% |
| Recall (Weighted) | 69.57% |
| F1-Score (Weighted) | 64.00% |
| Evaluation Samples | 115 |

### Topic Classifier

| Metric | Score |
|---|---:|
| Accuracy | 57.69% |
| Precision (Weighted) | 60.38% |
| Recall (Weighted) | 57.69% |
| F1-Score (Weighted) | 57.04% |
| Evaluation Samples | 126 |

*Note: Model Evaluation Metrics describe performance over the holdout test dataset, whereas Prediction Confidence describes the model's estimated probability for an individual input.*

---

## Limitations

- **Prototype Dataset Scale:** The models are trained on curated datasets (115 sentiment and 126 topic samples).
- **Spelling Diversity:** Romanized Gujarati exhibits extensive informal spelling variation; unmapped tokens are tagged as `Unknown`.
- **Classical Linear ML Bounds:** TF-IDF with Logistic Regression captures surface n-grams rather than deep transformer-level semantic context.
- **Topic Accuracy:** The topic classifier achieves 57.69% accuracy across 8 classes; predictions represent academic model estimates rather than definitive facts.
- **Confidence Diagnostics:** Inputs yielding < 60% confidence are honestly flagged with a low-confidence academic advisory.

---

## Academic Note

This system is an academic research demonstration and educational prototype designed to study Gujarati–English code-mixing dynamics, word-level language identification, and lightweight explainable NLP pipelines. All displayed probabilities, charts, and metrics are computed dynamically from actual model outputs without external AI APIs or simulated results.
