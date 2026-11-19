"""Tahmini risk skoru: son olaylara daha çok ağırlık veren, zamanla sönen toplam."""
from dataclasses import dataclass
from datetime import datetime, timezone

HALF_LIFE_DAYS = 14.0
KIND_WEIGHT = {"fight": 1.0, "assault": 2.0, "stabbing": 3.0}
LEVELS = [(0.5, "Sakin"), (2.0, "Hafif tedbirli"), (5.0, "Tedbirli"), (float("inf"), "Dikkatli ol")]

@dataclass
class Event:
    kind: str
    occurred_at: datetime
    confidence: float  # 0..1

def score(events, now=None):
    now = now or datetime.now(timezone.utc)
    total = 0.0
    for e in events:
        age_days = (now - e.occurred_at).total_seconds() / 86400
        decay = 0.5 ** (age_days / HALF_LIFE_DAYS)
        total += KIND_WEIGHT.get(e.kind, 1.0) * e.confidence * decay
    return total

def level(value):
    for limit, name in LEVELS:
        if value < limit:
            return name
