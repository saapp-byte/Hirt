"""ÖRNEK VERİ: gerçek olayları temsil etmez, yalnızca geliştirme içindir."""
from datetime import datetime, timedelta, timezone

NOW = datetime.now(timezone.utc)

AREAS = {
    1: {"name": "Moda", "district": "Kadıköy", "lat": 40.9867, "lng": 29.0256},
}

def _ago(days, hour):
    t = NOW - timedelta(days=days)
    return t.replace(hour=hour, minute=0, second=0, microsecond=0)

EVENTS = [
    {"id": 1, "area_id": 1, "kind": "fight", "occurred_at": _ago(3, 23), "lat": 40.9871, "lng": 29.0249,
     "source": "Haber kaynağı (örnek)", "confidence": 0.8},
    {"id": 2, "area_id": 1, "kind": "fight", "occurred_at": _ago(9, 1), "lat": 40.9860, "lng": 29.0262,
     "source": "Topluluk bildirimi (örnek)", "confidence": 0.5},
    {"id": 3, "area_id": 1, "kind": "assault", "occurred_at": _ago(20, 22), "lat": 40.9875, "lng": 29.0270,
     "source": "Haber kaynağı (örnek)", "confidence": 0.7},
]
