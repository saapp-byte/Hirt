"""Haber metninden olay saati, sokak, sonuç ve "eski olay/mahkeme haberi" bilgisi çıkarma (kural tabanlı).
Kişi adı çıkarılmaz ve saklanmaz."""
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "geo"))
from fold import fold  # noqa: E402

TR = timedelta(hours=3)  # Türkiye UTC+3 (yaz/kış saati yok)
RANK = {"dakika": 4, "saat": 3, "dilim": 2, "gun": 1, None: 0}

CLOCK = [
    re.compile(r"saat\s+(\d{1,2})[.:](\d{2})"),
    re.compile(r"\b(\d{1,2})[.:](\d{2})\s+(?:siralarinda|sularinda|civarinda|sirasinda)"),
]
HOUR_ONLY = re.compile(r"saat\s+(\d{1,2})(?:'|\s)?\s*(?:da|de|ta|te|siralarinda|sularinda|civarinda)\b")
STALE = [
    re.compile(r"\b\d+\s+yil\s+once\b"), re.compile(r"yildir\b"), re.compile(r"yillar\s+once"),
    re.compile(r"gecen\s+yil\b"), re.compile(r"\b\d+\s+ay\s+once\b"),
    re.compile(r"\b(dava|davasi|davasinda|durusma|durusmasi|iddianame|beraat|tahliye|mahkum|mahkeme|yargitay|istinaf)\b"),
    re.compile(r"hapis\s+cezasi|agirlastirilmis|cezaya\s+carptirildi|karar\s+verildi"),
]
STREET = re.compile(r"((?:[A-ZÇĞİÖŞÜ][\wçğıöşüÇĞİÖŞÜ.]+\s+){1,3}(?:Caddesi|Cadde|Sokağı|Sokak|Bulvarı|Bulvar|Meydanı|Mevkii))")
AREA_WORDS = {"Mahallesi", "Mahalle", "Mah.", "İlçesi", "Köyü", "Kasabası", "Belediyesi"}  # bundan öncesi sokak adı değil
STREET_STOP = {"Olay", "Saldırı", "Kavga", "Bıçaklı", "Silahlı", "Polis", "Jandarma", "Genç", "Adam", "Şahıs", "Sabah", "Akşam", "Gece"}

def stale_reason(text: str, published: datetime):
    """Eski olay / mahkeme / yakalama haberi mi? Nedenini döndürür, değilse None."""
    ft = fold(text)
    for rx in STALE:
        m = rx.search(ft)
        if m:
            return m.group(0)
    for m in re.finditer(r"\b(19\d\d|20\d\d)\s+(?:yilinda|tarihinde)\b", ft):
        if int(m.group(1)) <= published.year - 2:
            return m.group(0)
    return None

def _clock(ft):
    for rx in CLOCK:
        m = rx.search(ft)
        if m and int(m.group(1)) < 24 and int(m.group(2)) < 60:
            return int(m.group(1)), int(m.group(2)), "dakika"
    m = HOUR_ONLY.search(ft)
    if m and int(m.group(1)) < 24:
        return int(m.group(1)), 0, "saat"
    return None

def _day_offset(ft):
    if re.search(r"evvelki\s+gun|onceki\s+gun|iki\s+gun\s+once", ft):
        return -2
    if re.search(r"\bdun\b", ft):
        return -1
    if re.search(r"bu\s+(?:sabah|gece|aksam)|\bbugun\b|az\s+once|dakika\s+once|saatler\s+once|saat\s+once", ft):
        return 0
    return None

def _part(ft, off, pub_hour):
    if "sabaha karsi" in ft:
        return 4, "dilim"
    if "gece yarisi" in ft:
        return 0, "dilim"
    if re.search(r"\bgece\b", ft):
        return (23, "dilim") if off == -1 else (1, "dilim")
    for pat, h in ((r"\boglen|\bogle\b", 13), (r"ogleden\s+sonra|\bikindi", 15), (r"\baksam", 19), (r"\bsabah", 8)):
        if re.search(pat, ft):
            return h, "dilim"
    return None

def analyze(text: str, published: datetime):
    """text: başlık + özet + gövde başı. published: UTC. -> {occurred_at(UTC), time_precision, street, outcome}"""
    ft = fold(text)
    pub_tr = published + TR
    off = _day_offset(ft)
    clock = _clock(ft)
    hour = minute = None
    prec = None
    if clock:
        hour, minute, prec = clock
    else:
        part = _part(ft, off, pub_tr.hour)
        if part:
            hour, minute, prec = part[0], 0, part[1]
    occurred = published
    if hour is not None:
        d = off if off is not None else 0
        if off == -1 and hour < 6:  # "dün gece saat 02.30" -> bugünün gecesi
            d = 0
        base = pub_tr.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=d)
        if base > pub_tr + timedelta(minutes=30):
            base -= timedelta(days=1)
        occurred = base - TR
    elif off is not None:
        occurred, prec = published + timedelta(days=off), "gun"
    if not (published - timedelta(days=7) <= occurred <= published + timedelta(minutes=30)):
        occurred, prec = published, None  # mantıksızsa yayın zamanına dön
    street = None
    m = STREET.search(text)
    if m:
        words = m.group(1).split()
        for i in range(len(words) - 1, -1, -1):
            if words[i] in AREA_WORDS:
                words = words[i + 1:]
                break
        words = [w for w in words if w not in STREET_STOP]
        if len(words) >= 2:
            street = " ".join(words)
    lead = ft[:700]
    outcome = None
    if re.search(r"hayatini\s+kaybet|olduruldu|\boldu\b|can\s+verdi|olu\s+olarak", lead):
        outcome = "died"
    elif re.search(r"yaralandi|yarali|yaralanan", lead):
        outcome = "injured"
    return {"occurred_at": occurred, "time_precision": prec, "street": street, "outcome": outcome}
