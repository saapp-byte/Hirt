"""SQLite olay deposu. Aynı olayı anlatan haberler tek kayıtta birleşir."""
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "geo"))
from paths import DATA_DIR  # noqa: E402

from cluster import compatible, merge_place  # noqa: E402

DB_PATH = DATA_DIR / "events.db"
RANK = {"dakika": 4, "saat": 3, "dilim": 2, "gun": 1, None: 0}
SEV = {"died": 2, "injured": 1, None: 0}
NEW_COLS = {"street": "TEXT", "time_precision": "TEXT", "outcome": "TEXT"}

def connect(path=DB_PATH):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    cols = [r[1] for r in conn.execute("PRAGMA table_info(events)")]
    if cols and "province_id" not in cols:  # eski (yalnızca İstanbul) şema: veri yeniden üretilebilir
        conn.execute("DROP TABLE events")
        cols = []
    conn.execute("""CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY, kind TEXT NOT NULL, province_id INTEGER NOT NULL, district_id INTEGER,
        neighborhood_id INTEGER, lat REAL NOT NULL, lng REAL NOT NULL, precision TEXT NOT NULL, label TEXT NOT NULL,
        occurred_at TEXT NOT NULL, confidence REAL NOT NULL, sources TEXT NOT NULL,
        street TEXT, time_precision TEXT, outcome TEXT)""")
    for c, typ in NEW_COLS.items():  # eski veritabanını koruyarak göç
        if cols and c not in cols:
            conn.execute(f"ALTER TABLE events ADD COLUMN {c} {typ}")
    conn.execute("CREATE TABLE IF NOT EXISTS seen (url TEXT PRIMARY KEY, at TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS outlets (name TEXT PRIMARY KEY, url TEXT, n INTEGER NOT NULL DEFAULT 0)")
    return conn

def confidence_for(n_sources: int) -> float:
    return min(0.9, 0.5 + 0.1 * n_sources)  # 1 kaynak: 0.6, 2: 0.7, ... en çok 0.9

def best_time(a_iso, a_prec, b_iso, b_prec):
    """Daha kesin saati tercih et; eşitse en erkeni."""
    if RANK[a_prec] != RANK[b_prec]:
        return (a_iso, a_prec) if RANK[a_prec] > RANK[b_prec] else (b_iso, b_prec)
    return (min(a_iso, b_iso), a_prec or b_prec)

def seen_urls(conn):
    return {r[0] for r in conn.execute("SELECT url FROM seen")}

def mark_seen(conn, urls):
    now = datetime.now(timezone.utc).isoformat()
    conn.executemany("INSERT OR IGNORE INTO seen VALUES (?,?)", [(u, now) for u in urls])
    conn.commit()

def add_outlet(conn, name, url):
    conn.execute("INSERT OR IGNORE INTO outlets(name, url, n) VALUES (?,?,0)", (name, url))
    conn.execute("UPDATE outlets SET n = n + 1, url = COALESCE(NULLIF(url,''), ?) WHERE name=?", (url, name))

def upsert(conn, ev, window_hours=72):
    """ev: {id, kind, province_id, district_id, neighborhood_id, lat, lng, precision, label, occurred_at(iso),
    time_precision, street, outcome, sources:[{name,url,title}]}. Uyumlu ve 72 saat içindeki kayda birleşir."""
    t = datetime.fromisoformat(ev["occurred_at"])
    lo, hi = (t - timedelta(hours=window_hours)).isoformat(), (t + timedelta(hours=window_hours)).isoformat()
    keys = ("id", "province_id", "district_id", "neighborhood_id", "lat", "lng", "precision", "label",
            "occurred_at", "sources", "street", "time_precision", "outcome")
    rows = conn.execute(f"SELECT {','.join(keys)} FROM events WHERE kind=? AND province_id=? AND occurred_at BETWEEN ? AND ? "
                        "ORDER BY occurred_at", (ev["kind"], ev["province_id"], lo, hi)).fetchall()
    target = next((d for d in (dict(zip(keys, r)) for r in rows) if compatible(d, ev)), None)
    pk = ("province_id", "district_id", "neighborhood_id", "lat", "lng", "precision", "label")
    place = {k: ev[k] for k in pk}
    eid, sources = ev["id"], list(ev["sources"])
    occurred, tprec = ev["occurred_at"], ev.get("time_precision")
    street, outcome = ev.get("street"), ev.get("outcome")
    if target:
        eid = target["id"]
        occurred, tprec = best_time(occurred, tprec, target["occurred_at"], target["time_precision"])
        old = {k: target[k] for k in pk}
        merge_place(old, place)
        place = old
        street = target["street"] or street
        if SEV[target["outcome"]] > SEV[outcome]:
            outcome = target["outcome"]
        seen = {x["url"] for x in sources}
        sources += [x for x in json.loads(target["sources"]) if x["url"] not in seen]
    conn.execute(
        "INSERT OR REPLACE INTO events (id, kind, province_id, district_id, neighborhood_id, lat, lng, precision, label, "
        "occurred_at, confidence, sources, street, time_precision, outcome) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (eid, ev["kind"], place["province_id"], place["district_id"], place["neighborhood_id"], place["lat"],
         place["lng"], place["precision"], place["label"], occurred, confidence_for(len(sources)),
         json.dumps(sources, ensure_ascii=False), street, tprec, outcome))
    conn.commit()
