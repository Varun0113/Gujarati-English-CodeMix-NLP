"""Transliterator Module for Gujarati-English Code-Mixed Text.

Provides lightweight transliteration handling:
1. Recognizes Romanized Gujarati forms and maps them to canonical Romanized Gujarati representations.
2. Provides deterministic script transliteration for high-confidence canonical words.
3. Preserves original tokens when confidence is low or when tokens belong to other languages.
"""

# Deterministic transliteration dictionary for high-confidence common words
CANONICAL_GUJARATI_SCRIPT_MAP = {
    "aaje": "આજે",
    "aje": "આજે",
    "kaale": "કાલે",
    "kale": "કાલે",
    "mane": "મને",
    "mne": "મને",
    "tame": "તમે",
    "tme": "તમે",
    "tane": "તને",
    "tne": "તને",
    "bahu": "બહુ",
    "bau": "બહુ",
    "saru": "સારું",
    "saras": "સરસ",
    "chhe": "છે",
    "che": "છે",
    "chho": "છો",
    "nathi": "નથી",
    "nthi": "નથી",
    "hato": "હતો",
    "hati": "હતી",
    "hatu": "હતું",
    "hata": "હતા",
    "kem": "કેમ",
    "shu": "શું",
    "su": "શું",
    "maru": "મારું",
    "tamaru": "તમારું",
    "badha": "બધા",
    "lagyu": "લાગ્યું",
    "laagyu": "લાગ્યું",
    "maja": "મજા",
    "mast": "મસ્ત",
    "yaar": "યાર",
    "bhai": "ભાઈ",
    "aavyo": "આવ્યો",
    "aavi": "આવી",
    "gayo": "ગયો",
    "gayi": "ગઈ",
    "kharab": "ખરાબ",
    "samjay": "સમજાય",
    "gamti": "ગમતી",
    "gamyu": "ગમ્યું",
    "bilkul": "બિલકુલ"
}


def transliterate_token(token: str, to_script: bool = False) -> str:
    """Handle transliteration for a single token.

    If to_script is True and token is a recognized high-confidence Romanized Gujarati word,
    returns its Gujarati Unicode script representation.
    Otherwise, returns the normalized token preserving original form when confidence is low.
    """
    clean = token.strip().lower()
    if to_script and clean in CANONICAL_GUJARATI_SCRIPT_MAP:
        return CANONICAL_GUJARATI_SCRIPT_MAP[clean]
    return token


def get_token_transliteration(token: str, normalized: str, language: str) -> str:
    """Return the transliterated form for token-level analysis."""
    norm_clean = normalized.strip().lower()
    # If Romanized Gujarati, canonical transliteration is the normalized canonical form
    if language == "Romanized Gujarati":
        return norm_clean
    # If English or Gujarati script, preserve the normalized form
    return normalized


def transliterate_text(text: str, to_script: bool = False) -> str:
    """Handle text-level transliteration where high-confidence mappings exist."""
    if not text:
        return ""
    words = text.split()
    return " ".join([transliterate_token(w, to_script=to_script) for w in words])
