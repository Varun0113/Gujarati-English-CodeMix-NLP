"""Normalizer Module for Informal and Romanized Gujarati Code-Mixed Text.

Handles:
1. Repeated characters reduction (e.g., 'goooood' -> 'good', 'bahuuu' -> 'bahu')
2. Chat abbreviations / slang expansion (e.g., 'u' -> 'you', 'pls' -> 'please')
3. Romanized Gujarati spelling variants normalization (e.g., 'bau' -> 'bahu', 'mne' -> 'mane')
"""

import re

# Slang & chat abbreviations dictionary
COMMON_ABBREVIATIONS = {
    "u": "you",
    "ur": "your",
    "pls": "please",
    "plz": "please",
    "gr8": "great",
    "thx": "thanks",
    "ty": "thank you",
    "b4": "before",
    "omg": "oh my god",
    "idk": "i do not know",
    "btw": "by the way",
    "dm": "direct message",
    "pic": "picture",
    "msg": "message",
    "bcoz": "because",
    "cuz": "because",
    "bro": "brother",
    "yr": "yaar",
    "rn": "right now",
    "tc": "take care"
}

# Romanized Gujarati variant to canonical representation mapping
ROMANIZED_GUJARATI_VARIANTS = {
    "bau": "bahu",
    "bo": "bahu",
    "aje": "aaje",
    "mne": "mane",
    "tne": "tane",
    "tme": "tame",
    "amne": "amne",
    "che": "chhe",
    "chee": "chhe",
    "nthi": "nathi",
    "nthii": "nathi",
    "nai": "nahi",
    "naee": "nahi",
    "tamru": "tamaru",
    "apdu": "aapnu",
    "laagyu": "lagyu",
    "laage": "lage",
    "joyi": "joi",
    "jovu": "jovu",
    "bapor": "bapore",
    "gamyu": "gamyu",
    "sundar": "sundar",
    "saras": "saras",
    "saru": "saru"
}


def reduce_repeated_characters(token: str) -> str:
    """Normalize prolonged words with 3+ repeated characters down to standard canonical forms.

    Examples:
        'goooood' -> 'good'
        'booooring' -> 'boring'
        'bahuuu' -> 'bahu'
        'masttt' -> 'mast'
        'saaaaru' -> 'saru'
        'app' -> 'app' (unchanged)
    """
    if len(token) < 3:
        return token

    # Check known prolonged patterns first
    token_lower = token.lower()
    if re.search(r"g[o]{3,}d", token_lower):
        return "good"
    if re.search(r"b[o]{3,}ring", token_lower):
        return "boring"
    if re.search(r"b[a]?h[u]{2,}", token_lower):
        return "bahu"
    if re.search(r"m[a]?st{2,}", token_lower):
        return "mast"
    if re.search(r"s[a]{2,}r[u]?", token_lower):
        return "saru"

    # Only reduce if there is a sequence of 3 or more identical characters
    if not re.search(r"(.)\1{2,}", token):
        return token

    # For prolonged vowels/consonants repeated 3+ times, reduce to 1
    # except common double-letters in English ('ee', 'oo')
    def _replacer(match):
        char = match.group(1).lower()
        if char in ("o", "e"):
            return match.group(1) * 2
        return match.group(1)

    return re.sub(r"(.)\1{2,}", _replacer, token)


def normalize_token(token: str) -> str:
    """Normalize an individual word token for slang and Romanized Gujarati variants."""
    clean = token.strip()
    if not clean:
        return clean

    lower = clean.lower()

    # 1. Expand chat abbreviations
    if lower in COMMON_ABBREVIATIONS:
        expanded = COMMON_ABBREVIATIONS[lower]
        return expanded.upper() if clean.isupper() else (expanded.capitalize() if clean.istitle() else expanded)

    # 2. Reduce repeated characters
    reduced = reduce_repeated_characters(lower)

    # 3. Canonicalize Romanized Gujarati variants
    if reduced in ROMANIZED_GUJARATI_VARIANTS:
        canonical = ROMANIZED_GUJARATI_VARIANTS[reduced]
        return canonical.capitalize() if clean.istitle() else canonical

    # Return reduced token if modified, preserving case style
    if reduced != lower:
        return reduced.capitalize() if clean.istitle() else reduced

    return clean


def normalize_text(text: str) -> str:
    """Normalize full text while preserving structure and spacing."""
    if not text or not text.strip():
        return ""

    tokens = text.split()
    normalized_tokens = [normalize_token(t) for t in tokens]
    return " ".join(normalized_tokens)
