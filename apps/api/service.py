"""API mantığı (çerçeveden bağımsız). Hem dev_server.py hem main.py (FastAPI) bunu kullanır."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "risk"))

from risk import Event, level, score
from sample_data import AREAS, EVENTS

# Gün saatlerini 6 dilimde topla: 06-10, 10-16, 16-20, 20-00, 00-03, 03-06
BUCKETS = [(6, 10), (10, 16), (16, 20), (20, 24), (0, 3), (3, 6)]

def bucket_counts(events):
    counts = [0] * len(BUCKETS)
    for e in events:
        h = e["occurred_at"].hour
        for i, (a, b) in enumerate(BUCKETS):
            if a <= h < b:
                counts[i] += 1
                break
    return counts

def get_events():
    return [
        {"id": e["id"], "kind": e["kind"], "lat": e["lat"], "lng": e["lng"],
         "occurred_at": e["occurred_at"].isoformat(), "confidence": e["confidence"]}
        for e in EVENTS
    ]

def get_summary(area_id):
    area = AREAS.get(area_id)
    if not area:
        return None
    evs = [e for e in EVENTS if e["area_id"] == area_id]
    value = score([Event(e["kind"], e["occurred_at"], e["confidence"]) for e in evs])
    return {
        "name": area["name"], "district": area["district"],
        "level": level(value), "score": round(value, 2),
        "by_time": bucket_counts(evs),
        "events": [
            {"kind": e["kind"], "occurred_at": e["occurred_at"].isoformat(),
             "source": e["source"], "confidence": e["confidence"]}
            for e in sorted(evs, key=lambda x: x["occurred_at"], reverse=True)
        ],
        "sample_data": True,
    }
