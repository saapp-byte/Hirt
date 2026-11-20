"""Türkçe metin sadeleştirme (eşleştirme için)."""
import re

_TR = str.maketrans({
    "İ": "i", "I": "i", "ı": "i", "Ş": "s", "ş": "s", "Ğ": "g", "ğ": "g", "Ü": "u", "ü": "u",
    "Ö": "o", "ö": "o", "Ç": "c", "ç": "c", "Â": "a", "â": "a", "Î": "i", "î": "i", "Û": "u", "û": "u",
    "’": "'", "‘": "'",
})

def fold(text: str) -> str:
    """'Kadıköy'de' -> "kadikoy'de"."""
    return text.translate(_TR).lower()

def tokens(text: str):
    return [t for t in re.findall(r"[a-z0-9']+", fold(text)) if t.strip("'")]
