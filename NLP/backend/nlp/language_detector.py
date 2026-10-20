"""Language Detector Module for Gujarati-English Code-Mixed Text.

Identifies language at the word level:
- Gujarati (Gujarati script via Unicode range \u0A80-\u0AFF)
- English (controlled English lexicon & heuristics)
- Romanized Gujarati (controlled phonetic Roman Gujarati vocabulary)
- Unknown / Other (numbers, punctuation, unrecognized tokens)
"""

import re
import string

# Unicode range for Gujarati script: \u0A80 to \u0AFF
GUJARATI_UNICODE_PATTERN = re.compile(r"[\u0A80-\u0AFF]")

# Controlled lexicon of common English words
ENGLISH_LEXICON = {
    "a", "about", "above", "across", "actor", "action", "admission", "after", "again",
    "all", "almost", "also", "always", "am", "an", "and", "animation", "any", "app",
    "application", "appreciate", "are", "arrive", "arrival", "article", "as", "at",
    "athletes", "attendance", "audio", "average", "awesome", "back", "backup", "bad",
    "badminton", "bank", "baseball", "battery", "be", "beach", "beautiful", "because",
    "been", "before", "best", "better", "between", "big", "bike", "bill", "billing",
    "bitter", "black", "bluetooth", "board", "boat", "bollywood", "book", "booking",
    "boost", "boring", "both", "bottle", "bought", "breakfast", "broken", "brother",
    "budget", "bug", "bus", "but", "button", "buttons", "buy", "buying", "by", "cab",
    "cafe", "cake", "calendar", "call", "camera", "camp", "camping", "campus", "can",
    "cancel", "car", "card", "care", "cartoon", "cash", "celebration", "center",
    "certificate", "chai", "champion", "championship", "chance", "change", "channel",
    "chapter", "charge", "charging", "check", "checkout", "cheese", "chemistry",
    "cinema", "cinematography", "city", "class", "classes", "classroom", "clean",
    "clear", "clerk", "click", "client", "clock", "close", "clothes", "clothing",
    "cloud", "cloudy", "coach", "code", "coding", "coffee", "cold", "collaboration",
    "college", "color", "come", "comedy", "coming", "company", "competition", "complete",
    "computer", "concept", "concert", "conference", "connection", "cool", "copy",
    "couch", "counseling", "count", "counter", "course", "court", "cover", "crash",
    "creative", "cricket", "crime", "cup", "customer", "cut", "cyber", "daily",
    "damage", "dance", "danger", "dark", "data", "database", "date", "day", "days",
    "deadline", "dear", "decide", "decision", "deep", "delay", "delivery", "design",
    "designer", "dessert", "details", "device", "diet", "difficult", "digital",
    "dinner", "direct", "direction", "director", "dirty", "discount", "discounts",
    "discussion", "display", "doctor", "document", "documents", "dollar", "done",
    "door", "download", "down", "drama", "draw", "drawing", "drive", "driver", "drop",
    "due", "duty", "ear", "earbuds", "early", "easy", "eat", "eating", "economy",
    "education", "electric", "electricity", "electronic", "electronics", "email",
    "emergency", "emotional", "encryption", "end", "energy", "energetic", "engine",
    "engineer", "engineering", "english", "enjoy", "enter", "entertaining",
    "entertainment", "entry", "error", "event", "every", "everybody", "everyone",
    "exam", "examination", "excellent", "exchange", "excited", "exciting", "exhibition",
    "explain", "extra", "face", "fail", "failure", "family", "famous", "fan", "far",
    "fare", "fast", "father", "feature", "features", "fee", "feel", "feeling",
    "festival", "field", "fight", "file", "files", "film", "filter", "final", "find",
    "fine", "finish", "first", "fish", "fit", "fitness", "five", "fix", "flight",
    "floor", "folder", "food", "foot", "football", "for", "force", "form", "format",
    "forward", "four", "free", "fresh", "friday", "friend", "friends", "from", "front",
    "full", "fun", "function", "game", "games", "garden", "gas", "gate", "general",
    "gift", "give", "giving", "glass", "go", "goal", "goes", "going", "gold", "good",
    "grade", "great", "group", "grocery", "growth", "guide", "gym", "habit", "half",
    "hall", "hand", "hang", "happy", "hard", "hardware", "have", "he", "head",
    "healthy", "heart", "help", "helpful", "her", "here", "hero", "high", "highway",
    "hill", "him", "history", "hit", "hold", "holiday", "home", "hope", "hospital",
    "hostel", "hot", "hotel", "hour", "hours", "house", "how", "hub", "huge", "humor",
    "hurry", "husband", "hygiene", "ice", "idea", "identity", "image", "important",
    "improve", "in", "inc", "include", "income", "india", "information", "ink",
    "input", "inquiry", "inside", "install", "installation", "interest", "interface",
    "internet", "interview", "invoice", "is", "island", "issue", "it", "item", "items",
    "jacket", "jam", "jar", "job", "join", "joint", "journey", "joy", "joyful",
    "juice", "just", "kabaddi", "keep", "key", "keyboard", "kick", "kid", "kids",
    "kill", "kind", "king", "kitchen", "kit", "know", "lab", "laboratory", "lady",
    "lake", "lamp", "land", "lane", "language", "laptop", "large", "last", "late",
    "laugh", "launch", "law", "layer", "lazy", "lead", "leader", "league", "learn",
    "learning", "lecture", "left", "leg", "lesson", "level", "library", "life",
    "light", "line", "link", "lip", "list", "listen", "little", "live", "liver",
    "load", "local", "location", "lock", "log", "login", "long", "look", "lose",
    "loss", "lot", "love", "low", "luggage", "lunch", "machine", "mail", "main",
    "make", "mall", "man", "management", "manager", "many", "map", "marathon", "mark",
    "market", "marks", "match", "mate", "material", "math", "matter", "may", "me",
    "meal", "mean", "meat", "medal", "media", "medicine", "medium", "meet", "meeting",
    "melody", "member", "memory", "memorable", "men", "menu", "message", "metal",
    "method", "middle", "midnight", "midterm", "mile", "milk", "mind", "minute",
    "minutes", "miss", "mobile", "model", "modern", "money", "month", "monument",
    "monuments", "mood", "moon", "more", "morning", "most", "mother", "motion",
    "mountain", "mouse", "mouth", "move", "movie", "much", "music", "musical", "must",
    "my", "name", "nation", "natural", "nature", "near", "neat", "neck", "need",
    "negative", "network", "never", "new", "news", "newspaper", "next", "nice",
    "night", "no", "noise", "none", "noon", "north", "nose", "not", "note", "notes",
    "notice", "novel", "now", "number", "nut", "object", "ocean", "off", "offer",
    "office", "official", "offline", "oil", "old", "on", "once", "one", "online",
    "only", "open", "opening", "operating", "operation", "opinion", "order", "original",
    "other", "our", "out", "outdoor", "output", "over", "own", "pack", "package",
    "packet", "page", "pain", "paint", "pair", "paper", "papers", "parcel", "parents",
    "park", "part", "partner", "party", "pass", "passage", "passport", "password",
    "past", "path", "patience", "patient", "pay", "payment", "peaceful", "pen",
    "people", "perfect", "performance", "period", "person", "personal", "pet",
    "petrol", "phone", "photo", "physics", "pic", "pick", "picture", "pie", "piece",
    "pin", "pipe", "pitch", "pizza", "place", "places", "plan", "plane", "plant",
    "plastic", "plate", "platform", "play", "player", "pleasant", "please", "plus",
    "point", "police", "policy", "pool", "poor", "pop", "popular", "population",
    "port", "position", "positive", "post", "pot", "power", "practical", "practice",
    "precautions", "premium", "preparation", "prepare", "present", "presentation",
    "president", "press", "price", "print", "private", "prize", "problem", "procedure",
    "process", "processor", "produce", "product", "professor", "program", "project",
    "projector", "proper", "proud", "public", "pull", "pure", "push", "put", "quality",
    "queen", "question", "quick", "quiet", "race", "racing", "radio", "railway",
    "rain", "rate", "raw", "read", "ready", "real", "realistic", "really", "reason",
    "receipt", "receive", "recent", "recipe", "record", "recovery", "red", "reduce",
    "reference", "refresh", "registration", "regular", "relax", "relaxing", "release",
    "remember", "reminder", "remind", "remove", "rent", "repair", "repeat", "replace",
    "replacement", "report", "request", "require", "required", "rescue", "research",
    "reservation", "reset", "resort", "respect", "response", "restaurant", "result",
    "retro", "return", "review", "rice", "rich", "ride", "right", "ring", "river",
    "road", "role", "roll", "roof", "room", "root", "rope", "rose", "rough", "round",
    "route", "row", "rule", "rules", "run", "running", "rush", "sad", "safe", "safety",
    "sail", "salad", "salary", "sale", "salt", "same", "sample", "sand", "sandwich",
    "sandwiches", "save", "saving", "say", "scale", "scene", "scenery", "schedule",
    "scholarship", "school", "science", "scientist", "score", "screen", "sea",
    "search", "season", "seat", "second", "security", "see", "seed", "seek", "seem",
    "select", "selection", "sell", "seller", "semester", "send", "sense", "sentence",
    "series", "serious", "serve", "server", "service", "set", "setup", "seven",
    "several", "share", "sharp", "she", "sheet", "shelf", "shell", "shift", "shine",
    "ship", "shirt", "shoe", "shoes", "shop", "shopkeeper", "shopping", "short",
    "shortcut", "shortcuts", "shot", "should", "show", "shut", "sick", "side", "sight",
    "sign", "signal", "signature", "silence", "silver", "simple", "since", "sing",
    "singer", "single", "sister", "sit", "site", "situation", "six", "size", "skill",
    "skin", "skirt", "sky", "sleep", "slide", "slow", "small", "smart", "smile",
    "smoke", "smooth", "snack", "snow", "so", "soap", "social", "society", "sock",
    "soft", "software", "soil", "solid", "solution", "solve", "some", "son", "song",
    "songs", "soon", "sorry", "sound", "soup", "south", "space", "speak", "speaker",
    "special", "speed", "spell", "spend", "spicy", "sport", "sports", "spot", "spread",
    "spring", "square", "stadium", "staff", "stage", "stairs", "stamp", "stand",
    "standard", "star", "start", "state", "station", "statistics", "stay", "steady",
    "steak", "steam", "steel", "step", "steps", "stick", "still", "stock", "stomach",
    "stone", "stop", "store", "storm", "story", "straight", "strategy", "stream",
    "street", "strength", "stress", "strike", "strong", "structure", "structures",
    "struggle", "student", "students", "studio", "study", "stuff", "style", "subject",
    "submission", "submit", "successful", "such", "sudden", "sugar", "suit", "summer",
    "sun", "sunday", "super", "superb", "supermarket", "supply", "support", "sure",
    "surface", "surgery", "surprise", "sweet", "sweets", "sweater", "sweaters",
    "swim", "swimming", "switch", "sword", "syllabus", "sync", "system", "table",
    "tablet", "tail", "take", "taking", "talent", "talk", "tall", "tank", "target",
    "task", "taste", "tasty", "tax", "tea", "teach", "teacher", "teaching", "team",
    "tear", "technology", "telephone", "television", "tell", "temperature", "ten",
    "tennis", "tension", "term", "terminal", "terribly", "test", "testing", "text",
    "than", "thank", "thanks", "that", "the", "theater", "their", "them", "theme",
    "then", "there", "these", "they", "thick", "thin", "thing", "things", "think",
    "third", "this", "thriller", "thrilling", "throat", "through", "throw", "thumb",
    "ticket", "tickets", "tie", "time", "timetable", "timing", "timings", "tire",
    "title", "to", "toast", "today", "together", "tomato", "tomorrow", "tonight",
    "too", "tool", "tooth", "top", "topic", "toss", "touch", "tough", "tour",
    "tourism", "tourist", "tournament", "towel", "tower", "town", "track", "trade",
    "traditional", "traffic", "trailer", "train", "training", "transfer", "transport",
    "trash", "travel", "traveler", "treat", "treatment", "tree", "trekking", "trial",
    "trip", "trouble", "truck", "true", "trust", "truth", "try", "tube", "tune",
    "tunnel", "turn", "twelve", "twenty", "twice", "twin", "two", "type", "typical",
    "ugly", "uncle", "under", "understand", "unit", "united", "university", "unknown",
    "unlimited", "until", "up", "update", "upload", "upon", "upper", "upset", "urban",
    "urge", "use", "used", "useful", "user", "usual", "vacation", "valley", "value",
    "variety", "various", "vehicle", "version", "very", "victory", "video", "view",
    "village", "viral", "virus", "visa", "visit", "visitor", "voice", "volume",
    "vote", "voter", "vowel", "voyage", "wage", "wait", "waiting", "wake", "walk",
    "wall", "wallet", "war", "warm", "warn", "wash", "waste", "watch", "water",
    "waterfall", "waterfalls", "wave", "way", "we", "weak", "wear", "weather", "web",
    "wedding", "week", "weekend", "weekly", "weight", "welcome", "well", "west",
    "wet", "what", "wheel", "when", "where", "which", "while", "white", "who", "whole",
    "whose", "why", "wide", "wife", "wifi", "wild", "will", "win", "wind", "window",
    "wine", "wing", "winner", "winter", "wire", "wireless", "wisdom", "wise", "wish",
    "with", "within", "without", "woman", "women", "wonder", "wonderful", "wood",
    "word", "words", "work", "worker", "working", "workout", "world", "worry", "worth",
    "would", "wound", "wrap", "wreck", "wrist", "write", "writer", "writing", "wrong",
    "yard", "year", "years", "yellow", "yes", "yesterday", "yet", "you", "young",
    "your", "yours", "yourself", "zero", "zone", "zoo"
}

# Controlled lexicon of common Romanized Gujarati words and variants
ROMANIZED_GUJARATI_LEXICON = {
    # Pronouns & determiners
    "hu", "hun", "hnu", "mne", "mane", "mari", "maru", "maro", "mara", "maraa",
    "tme", "tame", "tne", "tane", "tari", "taru", "taro", "tara", "taraa",
    "tamaru", "tamri", "tamro", "tamra", "tamara", "tamari", "tamaro", "tamaro",
    "ame", "amne", "amari", "amaru", "amara", "amaro",
    "aapne", "aapna", "aapnu", "aapni", "apne", "apdu", "apda", "apdi",
    "te", "tenu", "teni", "teno", "tena", "tenae", "tene", "teva", "tevi",
    "teo", "emne", "temne", "badha", "badhi", "badhu", "badho", "badhaa",
    "aa", "pelu", "peli", "pelo", "pela", "koi", "koik", "koni", "konu", "kone", "kon",
    # Question words
    "shu", "su", "kem", "kemne", "kyare", "kare", "kya", "kyan", "kevi", "kevo",
    "kevu", "keva", "ketlu", "ketla", "ketli", "ketlo", "kae", "kai",
    # Verbs / auxiliaries
    "che", "chhe", "chho", "cho", "chhu", "chhum", "chee",
    "hato", "hati", "hatu", "hatum", "hata", "hataa",
    "nathi", "nthi", "nthii", "nai", "nahi", "naee", "naa", "na",
    "aavya", "aavyo", "aavi", "aavu", "aave", "aavse", "aavjo",
    "gayo", "gayi", "gayu", "gaya", "jaay", "jase", "javu", "jao",
    "kari", "karyu", "karo", "karta", "kare", "karshe", "karvanu", "karva",
    "karjo", "karvi", "karvo", "karya", "kidhu", "kahyu", "kehvu", "bolo",
    "bolya", "bole", "joyu", "joya", "joi", "jovu", "juo", "jota", "joiye", "joyiye",
    "lidho", "lidhi", "lidhu", "lidha", "levu", "leo", "leshe",
    "aapyu", "aapi", "aapo", "aapse", "aapvu", "aapya",
    "thayo", "thai", "thayu", "thaya", "thay", "thase", "thava",
    "samjyo", "samji", "samjay", "samjya", "samjavu",
    "gamti", "gamtu", "gamto", "gamta", "gamyu", "game",
    "lage", "lagyu", "lagi", "lagyo", "laagyu", "lagti", "lagto", "laage",
    "rahyo", "rahi", "rahyu", "rahya", "raho", "revanu",
    "mali", "malyo", "malyu", "malya", "malse", "malvu",
    "batav", "batavo", "batavya", "joyi", "mukyu", "muki", "mukyo",
    "vaparva", "vaparvu", "vaparyo", "farvu", "farya", "fari",
    # Adjectives, adverbs & qualifiers
    "saru", "saras", "bahu", "bau", "bo", "khoob", "khub", "ghano", "ghani", "ghanu", "ghana",
    "mast", "majama", "maja", "majano", "majani", "majahanu", "majedar",
    "thodu", "thodi", "thoda", "thodo", "dhire", "jaldi", "fatfat",
    "motu", "moti", "moto", "mota", "nanu", "nani", "nano", "nana",
    "khush", "khushi", "dukh", "dukhi", "pareshan", "pareshani", "bakwas", "bilkul",
    "kharab", "saachu", "khotu", "pure", "puro", "puri", "pura",
    "sundar", "unchi", "uncho", "unchu", "nichu", "nicho", "nichi",
    "swadist", "mithu", "tikhum", "tikhu", "garam", "thanduu", "thandu",
    "saf", "shant", "shanti", "chokhhu", "chokho",
    # Conjunctions & prepositions
    "ne", "ane", "pan", "pn", "to", "jo", "ke", "kemke", "karan", "mate",
    "sathe", "ma", "maa", "par", "ethi", "mathi", "sudhi", "vagar", "pachi", "pahela",
    "jem", "tem", "em", "evo", "evi", "evu", "eva", "jevo", "jevi", "jevu", "jeva",
    # Time, places & common nouns
    "aaje", "aje", "kaale", "kale", "roj", "divas", "raat", "savar", "savare",
    "bapor", "bapore", "sanj", "sanje", "samay", "vaar", "vakhat", "varas", "mahino",
    "ghar", "gher", "gaam", "gam", "shahar", "bajar", "raste", "rasto",
    "paisa", "rupiya", "khabar", "iccha", "vaat", "vaato", "varta", "vaarta",
    "vatavaran", "havaaman", "jivana", "jivan", "niam", "niyamo", "shaak", "rotli",
    "bhat", "daal", "dabeli", "sev", "usal", "dhokla", "adrak", "chhas", "mithai",
    "dosto", "bhai", "yaar", "ben", "ba", "bapu", "kaka", "kaki", "mama", "mami",
    "natak", "chokra", "chokri", "manas", "loko", "rit", "rite", "vibhag"
}


def is_gujarati_script(token: str) -> bool:
    """Check if token contains Gujarati script Unicode characters."""
    return bool(GUJARATI_UNICODE_PATTERN.search(token))


def is_english_token(token: str) -> bool:
    """Check if token belongs to English vocabulary or fits English lexical heuristics."""
    clean = token.lower().strip(string.punctuation)
    if not clean:
        return False
    if clean in ENGLISH_LEXICON:
        return True
    # English lexical pattern: only latin alphabetic characters, and ends with standard English inflectional suffixes
    if clean.isalpha():
        suffixes = ("tion", "sion", "ing", "ed", "able", "ible", "ment", "ness", "ity", "ful", "less", "ous")
        if any(clean.endswith(s) for s in suffixes) and len(clean) > 4:
            return True
    return False


def is_romanized_gujarati(token: str) -> bool:
    """Check if token matches Romanized Gujarati vocabulary or phonetic patterns."""
    clean = token.lower().strip(string.punctuation)
    if not clean:
        return False
    if clean in ROMANIZED_GUJARATI_LEXICON:
        return True
    # Common Gujarati Romanized verb inflection endings (e.g. karyo, kari, lagyu, aavya, gamti, hatu, nathi)
    inflections = ("yo", "yu", "ya", "vati", "vatu", "vano", "vana", "vani", "vaanu", "she", "se")
    if any(clean.endswith(inf) for inf in inflections) and len(clean) >= 4 and clean.isalpha():
        # Avoid false positives with genuine English words
        if clean not in ENGLISH_LEXICON:
            return True
    return False


def identify_word_language(word: str) -> str:
    """Identify the language category of a single word token.

    Returns:
        'Gujarati': for Gujarati Unicode script text
        'English': for English lexicon/words
        'Romanized Gujarati': for transliterated/phonetic Gujarati in Latin script
        'Unknown': for unrecognized words, symbols, or numbers
    """
    if not word or not word.strip():
        return "Unknown"

    cleaned = word.strip()

    # 1. Check for Gujarati script
    if is_gujarati_script(cleaned):
        return "Gujarati"

    # Strip punctuation and numbers for Latin-script classification
    alpha_clean = cleaned.strip(string.punctuation)
    if not alpha_clean or not any(c.isalpha() for c in alpha_clean):
        return "Unknown"

    # 2. Check Romanized Gujarati (priority on code-mixed markers)
    if is_romanized_gujarati(alpha_clean):
        return "Romanized Gujarati"

    # 3. Check English lexicon
    if is_english_token(alpha_clean):
        return "English"

    # 4. Fallback: unknown rather than guessing
    return "Unknown"


def compute_language_distribution(token_annotations: list) -> dict:
    """Calculate the language distribution percentages across a list of tokens."""
    # Filter out pure punctuation or empty tokens
    meaningful = [
        t for t in token_annotations
        if t["language"] in {"Gujarati", "Romanized Gujarati", "English", "Unknown"}
        and any(c.isalnum() for c in t["word"])
    ]

    total = len(meaningful)
    if total == 0:
        return {
            "Gujarati": 0.0,
            "Romanized Gujarati": 0.0,
            "English": 0.0,
            "Unknown": 0.0
        }

    counts = {
        "Gujarati": 0,
        "Romanized Gujarati": 0,
        "English": 0,
        "Unknown": 0
    }

    for item in meaningful:
        lang = item["language"]
        counts[lang] = counts.get(lang, 0) + 1

    return {lang: round((cnt / total) * 100.0, 1) for lang, cnt in counts.items()}
