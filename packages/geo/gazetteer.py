"""Yerel yer veritabanı (SQLite): il (81, yerleşik) + ilçe + mahalle (build_gazetteer.py ile indirilir).
Kimlikler: il = plaka (1-81); ilçe/mahalle = 1000 ve üstü."""
import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from fold import fold  # noqa: E402
from istanbul import DISTRICTS as ISTANBUL  # noqa: E402
from paths import DATA_DIR  # noqa: E402
from turkiye import PROVINCES  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = DATA_DIR / "places.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS places (
  id INTEGER PRIMARY KEY, level TEXT NOT NULL, name TEXT NOT NULL, folded TEXT NOT NULL,
  province_id INTEGER NOT NULL, district_id INTEGER, lat REAL NOT NULL, lng REAL NOT NULL,
  ambiguous INTEGER NOT NULL DEFAULT 0, osm_id TEXT);
CREATE INDEX IF NOT EXISTS ix_places_prov ON places(province_id, level);
CREATE INDEX IF NOT EXISTS ix_places_dist ON places(district_id);
CREATE TABLE IF NOT EXISTS aliases (folded TEXT NOT NULL, place_id INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS loaded (province_id INTEGER PRIMARY KEY, n_ilce INTEGER, n_mahalle INTEGER, at TEXT);
CREATE TABLE IF NOT EXISTS loaded_mah (district_id INTEGER PRIMARY KEY, n INTEGER, at TEXT);
"""

def connect(path=DB_PATH):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn

def seed(conn):
    """81 il + İstanbul'un 39 ilçesi (ağ gerektirmez)."""
    if conn.execute("SELECT COUNT(*) FROM places WHERE level='il'").fetchone()[0] >= len(PROVINCES):
        return
    for plate, name, lat, lng, aliases, amb in PROVINCES:
        conn.execute("INSERT OR IGNORE INTO places(id,level,name,folded,province_id,district_id,lat,lng,ambiguous) "
                     "VALUES (?,?,?,?,?,NULL,?,?,?)", (plate, "il", name, fold(name), plate, lat, lng, int(amb)))
        for a in aliases:
            conn.execute("INSERT INTO aliases VALUES (?,?)", (fold(a), plate))
    for d in ISTANBUL:
        pid = 1000 + d["id"]
        conn.execute("INSERT OR IGNORE INTO places(id,level,name,folded,province_id,district_id,lat,lng,ambiguous) "
                     "VALUES (?,?,?,?,34,?,?,?,?)", (pid, "ilce", d["name"], fold(d["name"]), pid, d["lat"], d["lng"], int(d["ambiguous"])))
        for a in d["aliases"]:
            conn.execute("INSERT INTO aliases VALUES (?,?)", (fold(a), pid))
    conn.commit()

def ensure(path=DB_PATH):
    conn = connect(path)
    seed(conn)
    return conn
