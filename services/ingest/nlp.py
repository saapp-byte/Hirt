"""Haber başlığından olay türü çıkarma (kural tabanlı, kurulum gerektirmez). Konum için locate.py."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "geo"))
from fold import fold, tokens  # noqa: E402,F401

# Bu kelimeler geçen başlıklar elenir (savaş haberi, spor, dizi, siber saldırı...)
EXCLUDE = {
    "mac", "maci", "macinda", "dizi", "dizisi", "film", "futbolcu", "taraftar", "taraftarlar", "oyuncu",
    "israil", "gazze", "ukrayna", "rusya", "iran", "suriye", "hamas", "lubnan", "filistin",
    "siber", "hacker", "konser", "sarkici", "transfer", "derbi", "lig",
}

# Öncelik sırasıyla: bıçaklama > saldırı > kavga
KIND_RULES = [
    ("stabbing", ["bicak"]),
    ("assault", ["saldiri", "saldirgan", "darp", "dovul", "silahla"]),
    ("fight", ["kavga", "yumruk", "arbede", "tekme"]),
]

def classify(title: str):
    text = fold(title)
    bases = {t.split("'")[0] for t in tokens(title)}
    if bases & EXCLUDE:
        return None
    for kind, keys in KIND_RULES:
        if any(k in text for k in keys):
            return kind
    return None

def classify_item(title: str, description: str = ""):
    """Önce başlık; olmazsa özetin ilk cümleleri."""
    return classify(title) or (classify(description[:250]) if description else None)
