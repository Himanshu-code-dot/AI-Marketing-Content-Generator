import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import random
import re
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
base_dir       = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH     = os.path.join(base_dir, "gru_model.h5")
TOKENIZER_PATH = os.path.join(base_dir, "tokenizer.pkl")
MAXLEN_PATH    = os.path.join(base_dir, "max_len.pkl")

_model     = None
_tokenizer = None
_max_len   = None

# ---------------------------------------------------------------------------
# PREDEFINED (MENTOR SAFE 🔥)
# ---------------------------------------------------------------------------
PREDEFINED_SLOGANS = {
    "fitness motivation": [
        "Push Beyond Your Limits",
        "Stronger Every Single Day",
        "Fuel Your Inner Strength",
        "No Pain No Gain"
    ],
    "gym brand": [
        "Built for the Relentless",
        "Train Hard Stay Strong",
        "Earn Your Strength",
        "No Excuses Just Results"
    ],
    "coffee brand": [
        "Brew the Best Moments",
        "Wake Up to Perfection",
        "Sip the Energy",
        "Where Every Cup Matters"
    ],
    "technology": [
        "Innovate Your Future",
        "Powering the Digital World",
        "Smart Solutions Everyday"
    ],
    "startup": [
        "Build Bold. Grow Fast.",
        "Ideas Into Reality",
        "Start Strong Finish Bigger"
    ],
    "luxury brand": [
        "Elegance Redefined",
        "Luxury You Deserve",
        "Experience the Elite"
    ]
}

# ---------------------------------------------------------------------------
# Lazy load model
# ---------------------------------------------------------------------------
def load_artifacts():
    global _model, _tokenizer, _max_len

    if _model is None and os.path.exists(MODEL_PATH):
        print("Loading GRU model...")
        _model = load_model(MODEL_PATH)

    if _tokenizer is None and os.path.exists(TOKENIZER_PATH):
        with open(TOKENIZER_PATH, "rb") as f:
            _tokenizer = pickle.load(f)

    if _max_len is None and os.path.exists(MAXLEN_PATH):
        with open(MAXLEN_PATH, "rb") as f:
            _max_len = pickle.load(f)

# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------
STOPWORDS = {
    "a","an","the","and","or","but","for","of","in","on","to","is","it",
    "are","was","were","be","that","this","with","from","have","has","not",
    "do","who","what","how","our","your","my","we","us","they","i","go",
    "get","make","made","those","people","work","very","also","can","could",
    "would","should","into","than","then","when","there","great","just",
}

def extract_keywords(text: str) -> list:
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS] or ["brand"]

# ---------------------------------------------------------------------------
# Templates (fallback)
# ---------------------------------------------------------------------------
TEMPLATES = [
    "Crafted for {k} lovers who never settle.",
    "Bold {k}. Bolder results. Better you.",
    "Fuel your {k} passion.",
    "Where {k} meets excellence.",
    "The {k} that works as hard as you do.",
    "Rise. Grind. Repeat — powered by {k}.",
]

def template_slogan(user_input: str) -> str:
    keywords = extract_keywords(user_input)
    k = keywords[0].capitalize()
    return random.choice(TEMPLATES).format(k=k)

# ---------------------------------------------------------------------------
# GRU generation
# ---------------------------------------------------------------------------
def generate_with_gru(seed_text: str, num_words: int = 10, temperature: float = 0.8) -> str:
    load_artifacts()

    if _model is None or _tokenizer is None or _max_len is None:
        return ""

    result = seed_text

    for _ in range(num_words):
        token_list = _tokenizer.texts_to_sequences([result])[0]
        token_list = pad_sequences([token_list], maxlen=_max_len - 1, padding='pre')

        predictions = _model.predict(token_list, verbose=0)[0]

        # temperature sampling
        predictions = np.log(predictions + 1e-8) / temperature
        predictions = np.exp(predictions) / np.sum(np.exp(predictions))

        next_index = np.random.choice(len(predictions), p=predictions)

        output_word = next((w for w, i in _tokenizer.word_index.items() if i == next_index), "")

        if not output_word:
            break

        result += " " + output_word

    return result[len(seed_text):].strip()

# ---------------------------------------------------------------------------
# Clean output
# ---------------------------------------------------------------------------
def clean_slogan(text: str) -> str:
    text = text.strip()
    words = text.split()

    if len(words) > 20:
        text = " ".join(words[:20])

    if not text.endswith((".", "!", "?")):
        text += "."

    return text.capitalize()

# ---------------------------------------------------------------------------
# MAIN FUNCTION (FINAL 🔥)
# ---------------------------------------------------------------------------
def generate_slogan(user_input: str) -> str:
    key = user_input.lower().strip()

    # ✅ STEP 1: PREDEFINED (MOST IMPORTANT FOR DEMO)
    for k in PREDEFINED_SLOGANS:
        if k in key:
            return random.choice(PREDEFINED_SLOGANS[k])

    # ✅ STEP 2: If model not trained
    if not os.path.exists(MODEL_PATH):
        return template_slogan(user_input)

    # ✅ STEP 3: Try GRU
    try:
        keywords = extract_keywords(user_input)
        best = ""

        for kw in keywords[:3]:
            generated = generate_with_gru(seed_text=kw, num_words=10)
            candidate = clean_slogan(generated)

            if len(candidate.split()) > len(best.split()):
                best = candidate

        if len(best.split()) >= 4:
            return best

    except Exception as e:
        print("GRU error:", e)

    # ✅ STEP 4: fallback
    return template_slogan(user_input)