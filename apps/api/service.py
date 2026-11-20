"""API mantığı (çerçeveden bağımsız). Türkiye geneli: il -> ilçe -> mahalle.
Gerçek veri varsa onu, yoksa örnek veriyi kullanır."""
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path += [str(ROOT / "packages" / "risk"), str(ROOT / "packages" / "geo")]

import gazetteer  # noqa: E402
from paths import DATA_DIR  # noqa: E402
from risk import Event, level, score  # noqa: E402
import sample_data  # noqa: E402

DB_PATH = DATA_DIR / "events.db"
WINDOW_DAYS = 30
NO_NEWS = "Kayıt yok"  # kayıt bulunamadı != güvenli

# Gün saatlerini 6 dilimde topla: 06-10, 10-16, 16-20, 20-00, 00-03, 03-06
BUCKETS = [(6, 10), (10, 16), (16, 20), (20, 24), (0, 3), (3, 6)]

def bucket_counts(events):
    counts = [0] * len(BUCKETS)
    for e in events:
        h = (e["occurred_at"] + timedelta(hours=3)).hour  # Türkiye saati
        for i, (a, b) in enumerate(BUCKETS):
            if a <= h < b:
                counts[i] += 1
                break
    return counts

def _load():
    """(olaylar, örnek_mi). Veritabanında kayıt yoksa örnek veri kullanılır."""
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH, timeout=30)
        base = "id, kind, province_id, district_id, neighborhood_id, lat, lng, precision, label, occurred_at, confidence, sources"
        try:
            rows = conn.execute(f"SELECT {base}, street, time_precision, outcome FROM events").fetchall()
        except sqlite3.OperationalError:
            try:  # ingest henüz yeni şemaya geçirmediyse (eski sütunlar)
                rows = [r + (None, None, None) for r in conn.execute(f"SELECT {base} FROM events").fetchall()]
            except sqlite3.OperationalError:  # çok eski şema: yeniden tarama gerekir
                rows = []
        conn.close()
        if rows:
            out = []
            for id_, kind, pid, did, nid, lat, lng, prec, label, occ, conf, src, street, tprec, outcome in rows:
                sources = json.loads(src)
                names = [s["name"] for s in sources]
                out.append({"id": id_, "kind": kind, "province_id": pid, "district_id": did, "neighborhood_id": nid,
                            "lat": lat, "lng": lng, "precision": prec, "label": label,
                            "occurred_at": datetime.fromisoformat(occ), "confidence": conf,
                            "source": names[0] + (f" +{len(names) - 1} kaynak" if len(names) > 1 else ""),
                            "url": sources[0]["url"], "street": street, "time_precision": tprec, "outcome": outcome})
            return out, False
    out = [dict(e, province_id=34, district_id=1001, neighborhood_id=None, precision="ilce",
                label="Kadıköy, İstanbul", url=None, street=None, time_precision="saat", outcome=None) for e in sample_data.EVENTS]
    return out, True

def _recent(events):
    cutoff = datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)
    return [e for e in events if e["occurred_at"] >= cutoff]

def _value(evs):
    return score([Event(e["kind"], e["occurred_at"], e["confidence"]) for e in evs])

def _events_for(evs, place):
    key = {"il": "province_id", "ilce": "district_id", "mahalle": "neighborhood_id"}[place["level"]]
    return [e for e in evs if e[key] == place["id"]]

COLS = "id, level, name, province_id, district_id, lat, lng"

def _place(conn, pid):
    r = conn.execute(f"SELECT {COLS} FROM places WHERE id=?", (pid,)).fetchone()
    return dict(zip(("id", "level", "name", "province_id", "district_id", "lat", "lng"), r)) if r else None

def _area_row(place, mine, sample):
    v = _value(mine)
    return {"id": place["id"], "name": place["name"], "lat": place["lat"], "lng": place["lng"],
            "place_level": place["level"], "level": level(v) if mine else NO_NEWS, "score": round(v, 2),
            "count": len(mine), "sample_data": sample}

def get_events():
    evs, _ = _load()
    return [{"id": e["id"], "kind": e["kind"], "lat": e["lat"], "lng": e["lng"], "precision": e["precision"],
             "occurred_at": e["occurred_at"].isoformat(), "confidence": e["confidence"]} for e in _recent(evs)]

def get_areas(parent=None):
    """parent yoksa 81 il; il verilirse ilçeleri; ilçe verilirse olay olan mahalleleri."""
    conn = gazetteer.ensure()
    evs, sample = _load()
    evs = _recent(evs)
    if parent is None:
        rows = conn.execute(f"SELECT {COLS} FROM places WHERE level='il'").fetchall()
    else:
        p = _place(conn, parent)
        if not p:
            return []
        col = {"il": ("ilce", "province_id"), "ilce": ("mahalle", "district_id")}.get(p["level"])
        if not col:
            return []
        rows = conn.execute(f"SELECT {COLS} FROM places WHERE level=? AND {col[1]}=?", (col[0], parent)).fetchall()
    out = []
    for r in rows:
        place = dict(zip(("id", "level", "name", "province_id", "district_id", "lat", "lng"), r))
        mine = _events_for(evs, place)
        if place["level"] == "mahalle" and not mine:
            continue  # binlerce mahalleyi listelemek yerine yalnızca olay olanları göster
        out.append(_area_row(place, mine, sample))
    out.sort(key=lambda a: (-a["score"], a["name"]))
    return out

def get_summary(area_id):
    conn = gazetteer.ensure()
    place = _place(conn, area_id)
    if not place:
        return None
    evs, sample = _load()
    mine = _events_for(_recent(evs), place)
    v = _value(mine) if mine else 0.0
    timed = [e for e in mine if e.get("time_precision") in ("dakika", "saat", "dilim")]
    time_ok = len(timed) >= 3 and len(timed) >= 0.5 * len(mine)
    if place["level"] == "il":
        parent = "Türkiye"
    else:
        names = []
        if place["level"] == "mahalle" and place["district_id"]:
            names.append(_place(conn, place["district_id"])["name"])
        names.append(_place(conn, place["province_id"])["name"])
        parent = ", ".join(names)
    return {
        "name": place["name"], "district": parent, "place_level": place["level"],
        "level": level(v) if mine else NO_NEWS, "score": round(v, 2),
        # Saat dağılımı yalnızca haberde saati/dilimi yazan olaylardan hesaplanır; yeterli sayıda yoksa gizlenir.
        "time_reliable": sample or time_ok, "timed_count": len(timed),
        "by_time": bucket_counts(timed) if (sample or time_ok) else [0] * 6,
        "window_days": WINDOW_DAYS, "event_count": len(mine),
        "events": [
            {"kind": e["kind"], "occurred_at": e["occurred_at"].isoformat(), "place": e["label"],
             "precision": e["precision"], "street": e.get("street"), "time_precision": e.get("time_precision"),
             "outcome": e.get("outcome"), "source": e["source"], "url": e["url"], "confidence": e["confidence"]}
            for e in sorted(mine, key=lambda x: x["occurred_at"], reverse=True)
        ],
        "sample_data": sample,
    }
