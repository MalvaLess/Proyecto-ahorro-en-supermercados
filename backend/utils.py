import unicodedata
import re

STOPWORDS = {"de", "la", "el", "los", "las", "un", "una", "y", "con", "sin", "para", "por", "del"}


def normalize_brand(name):
    if not name:
        return ""
    name = name.lower().strip()
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    return name


def _tokens(text):
    words = re.sub(r"[^\w\s]", "", text.lower()).split()
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def jaccard_similarity(name1, name2):
    t1, t2 = _tokens(name1), _tokens(name2)
    if not t1 or not t2:
        return 0.0
    return len(t1 & t2) / len(t1 | t2)


_WEIGHT_RE = re.compile(r'\d+\s*(?:g|gr|kg|ml|l|lt|cc|mg|oz|un)\b', re.IGNORECASE)

def _weight_tokens(text):
    return {re.sub(r'\s+', '', m.lower()) for m in _WEIGHT_RE.findall(text)}

def same_size(name1, name2):
    """False si ambos nombres tienen tokens de peso/cantidad distintos."""
    w1, w2 = _weight_tokens(name1), _weight_tokens(name2)
    if w1 and w2 and not (w1 & w2):
        return False
    return True


