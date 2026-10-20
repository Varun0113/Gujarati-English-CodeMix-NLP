"""NLP Pipeline Module for Gujarati-English Code-Mixed Text.

Coordinates:
1. Raw Text Cleaning & Tokenization
2. Word-Level Language Identification
3. Informal Text Normalization & Transliteration
4. Language Distribution & Transitions
5. Text & Normalization Statistics
6. Supervised ML Classification (Sentiment & Topic with full probability distributions)
7. Deterministic Research Insights & Confidence Diagnostics
"""

import re
import string
from nlp.classifier import predict_sentiment_full, predict_topic_full
from nlp.language_detector import compute_language_distribution, identify_word_language
from nlp.normalizer import normalize_text, normalize_token
from nlp.transliterator import get_token_transliteration, transliterate_token


def tokenize(text: str) -> list:
    """Tokenize code-mixed text while preserving Gujarati Unicode characters and punctuation."""
    if not text:
        return []
    # Split on whitespace while preserving words with Gujarati characters, hyphens, and apostrophes
    tokens = re.findall(r"[\u0A80-\u0AFFa-zA-Z0-9']+|[^\s\w]", text)
    return tokens


def is_word_token(token: str) -> bool:
    """Check if token contains alphanumeric or Gujarati script characters."""
    return any(c.isalnum() or '\u0A80' <= c <= '\u0AFF' for c in token)


def analyze_text(text: str) -> dict:
    """Run full academic NLP research pipeline on Gujarati-English code-mixed input.

    Args:
        text (str): Input text (e.g. 'Aaje college ma bau boring lecture hato')

    Returns:
        dict: Complete structured analysis result.
    """
    original_text = text.strip() if text else ""
    if not original_text:
        return {
            "original_text": "",
            "normalized_text": "",
            "is_normalized_identical": True,
            "tokens": [],
            "language_distribution": {
                "Gujarati": 0.0,
                "Romanized Gujarati": 0.0,
                "English": 0.0,
                "Unknown": 0.0
            },
            "language_counts": {
                "Gujarati": 0,
                "Romanized Gujarati": 0,
                "English": 0,
                "Unknown": 0
            },
            "statistics": {
                "characters": 0,
                "total_tokens": 0,
                "unique_tokens": 0,
                "normalized_tokens": 0,
                "gujarati_tokens": 0,
                "english_tokens": 0,
                "romanized_tokens": 0,
                "unknown_tokens": 0,
                "avg_token_length": 0.0
            },
            "code_mixing": {
                "dominant_language": "None",
                "is_mixed": False,
                "mixing_label": "No",
                "language_count": 0
            },
            "language_transitions": {
                "sequence": [],
                "short_sequence": "None",
                "transitions": []
            },
            "normalization_comparison": {
                "tokens_changed_count": 0,
                "total_word_tokens": 0,
                "changes": []
            },
            "sentiment": {
                "label": "Neutral",
                "confidence": 0.0,
                "probabilities": {"Positive": 33.3, "Neutral": 33.3, "Negative": 33.3}
            },
            "topic": {
                "label": "General",
                "confidence": 0.0,
                "probabilities": {"General": 100.0}
            },
            "sentiment_confidence": 0.0,
            "topic_confidence": 0.0,
            "unknown_tokens": [],
            "research_insights": "No text provided for analysis.",
            "confidence_assessment": {
                "status": "low",
                "message": "No input text provided."
            }
        }

    # Step 1: Tokenization
    raw_tokens = tokenize(original_text)

    # Step 2 & 3: Word-level identification, normalization, and transliteration
    tokens_meta = []
    word_tokens = []
    norm_comparison_list = []
    unknown_words = []

    for raw in raw_tokens:
        is_word = is_word_token(raw)
        lang = identify_word_language(raw) if is_word else "Punctuation"
        norm = normalize_token(raw) if is_word else raw

        # If language was initially unknown, re-check normalized token
        if lang == "Unknown" and norm != raw:
            updated_lang = identify_word_language(norm)
            if updated_lang != "Unknown":
                lang = updated_lang

        translit = get_token_transliteration(raw, norm, lang) if is_word else raw

        token_entry = {
            "token": raw,
            "word": raw,  # backward compatibility
            "language": lang,
            "normalized": norm,
            "transliteration": translit
        }
        tokens_meta.append(token_entry)

        if is_word:
            word_tokens.append(raw)
            changed = (raw.strip().lower() != norm.strip().lower())
            norm_comparison_list.append({
                "original": raw,
                "normalized": norm,
                "changed": changed
            })
            if lang == "Unknown":
                cleaned_unknown = raw.strip(string.punctuation)
                if cleaned_unknown and cleaned_unknown not in unknown_words:
                    unknown_words.append(cleaned_unknown)

    # Step 4: Text Normalization reconstruction
    normalized_text = normalize_text(original_text)
    is_identical = (original_text.strip() == normalized_text.strip())

    # Step 5: Language distribution & counts
    distribution = compute_language_distribution(tokens_meta)

    # Exact language token counts
    lang_counts = {
        "Gujarati": 0,
        "Romanized Gujarati": 0,
        "English": 0,
        "Unknown": 0
    }
    for t in tokens_meta:
        if t["language"] in lang_counts:
            lang_counts[t["language"]] += 1

    # Step 6: Text Statistics
    total_words = len(word_tokens)
    unique_words = len(set(w.lower() for w in word_tokens))
    tokens_changed = sum(1 for c in norm_comparison_list if c["changed"])
    avg_length = round(sum(len(w) for w in word_tokens) / total_words, 1) if total_words > 0 else 0.0

    stats = {
        "characters": len(original_text),
        "total_tokens": total_words,
        "unique_tokens": unique_words,
        "normalized_tokens": tokens_changed,
        "gujarati_tokens": lang_counts["Gujarati"],
        "english_tokens": lang_counts["English"],
        "romanized_tokens": lang_counts["Romanized Gujarati"],
        "unknown_tokens": lang_counts["Unknown"],
        "avg_token_length": avg_length
    }

    # Step 7: Code-mixing Analysis
    # Recognized languages: Gujarati, Romanized Gujarati, English
    recognized_counts = {
        "English": lang_counts["English"],
        "Romanized Gujarati": lang_counts["Romanized Gujarati"],
        "Gujarati": lang_counts["Gujarati"]
    }
    present_langs = [l for l, cnt in recognized_counts.items() if cnt > 0]
    dominant_lang = max(recognized_counts.items(), key=lambda x: x[1])[0] if any(recognized_counts.values()) else "None"
    is_mixed = len(present_langs) > 1

    code_mixing = {
        "dominant_language": dominant_lang,
        "is_mixed": is_mixed,
        "mixing_label": "Yes" if is_mixed else "No",
        "language_count": len(present_langs)
    }

    # Step 8: Language Transition Analysis
    code_map = {
        "English": "EN",
        "Gujarati": "GU",
        "Romanized Gujarati": "RG",
        "Unknown": "UN"
    }
    meaningful_tokens = [t for t in tokens_meta if t["language"] in code_map]
    lang_seq = [t["language"] for t in meaningful_tokens]
    short_seq = " → ".join([code_map.get(l, l) for l in lang_seq]) if lang_seq else "None"

    # Count consecutive transitions
    transition_counts = {}
    for i in range(len(lang_seq) - 1):
        l1, l2 = lang_seq[i], lang_seq[i + 1]
        if l1 != l2:
            key = f"{l1} → {l2}"
            transition_counts[key] = transition_counts.get(key, 0) + 1

    transition_list = [
        {"from": k.split(" → ")[0], "to": k.split(" → ")[1], "transition": k, "count": v}
        for k, v in sorted(transition_counts.items(), key=lambda x: x[1], reverse=True)
    ]

    language_transitions = {
        "sequence": lang_seq,
        "short_sequence": short_seq,
        "transitions": transition_list
    }

    # Step 9: ML Classification (Full probabilities)
    sentiment_data = predict_sentiment_full(normalized_text)
    topic_data = predict_topic_full(normalized_text)

    # Step 10: Deterministic Research Insights
    min_confidence = min(sentiment_data["confidence"], topic_data["confidence"])
    if is_mixed:
        langs_str = ", ".join(present_langs)
        insight_p1 = f"The input contains tokens from multiple language categories ({langs_str}), confirming active code-mixing."
    else:
        insight_p1 = f"The input is predominantly in {dominant_lang} with no significant code-mixing detected."

    insight_p2 = f"Dominant language: {dominant_lang} ({distribution.get(dominant_lang, 0)}% of classified tokens)."
    insight_p3 = f"The sentiment classifier predicts '{sentiment_data['label']}' with {sentiment_data['confidence']}% model confidence."
    insight_p4 = f"The topic classifier identifies '{topic_data['label']}' with {topic_data['confidence']}% model confidence."

    if min_confidence < 60.0:
        conf_status = "low"
        conf_msg = "Low Confidence: One or more predictions have model confidence below 60%. Consider these results as an academic model estimate rather than a definitive classification."
    else:
        conf_status = "solid"
        conf_msg = "Model prediction confidence is relatively strong (≥ 60%) across evaluated TF-IDF feature weights."

    full_insights = f"{insight_p1} {insight_p2} {insight_p3} {insight_p4}"

    return {
        "original_text": original_text,
        "normalized_text": normalized_text,
        "is_normalized_identical": is_identical,
        "tokens": tokens_meta,
        "language_distribution": distribution,
        "language_counts": lang_counts,
        "statistics": stats,
        "code_mixing": code_mixing,
        "language_transitions": language_transitions,
        "normalization_comparison": {
            "tokens_changed_count": tokens_changed,
            "total_word_tokens": total_words,
            "changes": norm_comparison_list
        },
        "sentiment": sentiment_data,
        "topic": topic_data,
        # Backward compatibility aliases
        "sentiment_label": sentiment_data["label"],
        "sentiment_confidence": sentiment_data["confidence"],
        "topic_label": topic_data["label"],
        "topic_confidence": topic_data["confidence"],
        "unknown_tokens": unknown_words,
        "research_insights": full_insights,
        "confidence_assessment": {
            "status": conf_status,
            "message": conf_msg,
            "min_confidence": min_confidence
        }
    }
