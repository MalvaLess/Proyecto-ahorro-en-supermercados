import unicodedata
import re

STOPWORDS = {"de", "la", "el", "los", "las", "un", "una", "y", "con", "sin", "para", "por", "del"}

# Pares (patrón, reemplazo) aplicados antes de tokenizar — orden importa
_SYNONYMS = [
    (re.compile(r'\bsin\s+az[uú]car\b', re.IGNORECASE), 'sinazucar'),
    (re.compile(r'\bzero\b',            re.IGNORECASE), 'sinazucar'),
    (re.compile(r'\bdiet\b',            re.IGNORECASE), 'light'),
]

# Captura cantidades con o sin decimal: "500 G", "1.5 L", "2,5kg"
_UNIT_NORM_RE = re.compile(
    r'(\d+(?:[.,]\d+)?)\s*(g|gr|kg|ml|l|lt|cc|mg|oz|un)\b',
    re.IGNORECASE
)

# Para same_size / _weight_tokens (igual que antes, mantiene compatibilidad)
_WEIGHT_RE = re.compile(r'\d+(?:[.,]\d+)?\s*(?:g|gr|kg|ml|l|lt|cc|mg|oz|un)\b', re.IGNORECASE)


def normalize_brand(name):
    if not name:
        return ""
    name = name.lower().strip()
    # Reemplaza guiones con espacio: "Coca-Cola" → "coca cola"
    name = name.replace('-', ' ')
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    name = re.sub(r'\s+', ' ', name).strip()
    return name


def _ean13_checksum_ok(s):
    total = sum((3 if i % 2 else 1) * int(d) for i, d in enumerate(s[:12]))
    return (10 - total % 10) % 10 == int(s[12])


def ean13_valido(code):
    """Valida EAN-13: 13 dígitos, no empieza en 2, checksum correcto."""
    s = str(code).strip() if code else ""
    if len(s) != 13 or not s.isdigit() or s.startswith("2"):
        return False
    return _ean13_checksum_ok(s)


def _normalize_for_tokens(text):
    """Preprocesa texto antes de tokenizar: diacríticos, unidades y sinónimos."""
    text = text.lower()
    # Quitar diacríticos: "azúcar" → "azucar"
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    # Normalizar unidades con espacio: "500 G" → "500g", "1.5 L" → "1.5l"
    text = _UNIT_NORM_RE.sub(lambda m: m.group(1).replace(',', '.') + m.group(2).lower(), text)
    # Sinónimos: "Zero" → "sinazucar", "Sin Azúcar" → "sinazucar", "Diet" → "light"
    for pattern, replacement in _SYNONYMS:
        text = pattern.sub(replacement, text)
    return text


def _tokens(text):
    text = _normalize_for_tokens(text)
    words = re.sub(r"[^\w\s]", "", text).split()
    return {w for w in words if len(w) > 2 and w not in STOPWORDS}


def jaccard_similarity(name1, name2):
    t1, t2 = _tokens(name1), _tokens(name2)
    if not t1 or not t2:
        return 0.0
    return len(t1 & t2) / len(t1 | t2)


def _weight_tokens(text):
    return {re.sub(r'\s+', '', m.lower()) for m in _WEIGHT_RE.findall(text)}


def same_size(name1, name2):
    """False si ambos nombres tienen tokens de peso/cantidad distintos."""
    w1, w2 = _weight_tokens(name1), _weight_tokens(name2)
    if w1 and w2 and not (w1 & w2):
        return False
    return True
