"""İlçe bazlı mahalle yükleme: ağ yok, sahte Overpass yanıtıyla."""
import os, sys, tempfile
from pathlib import Path
os.environ["HIRT_DATA_DIR"] = tempfile.mkdtemp()
HERE = Path(__file__).resolve().parent
sys.path += [str(HERE), str(HERE.parents[1] / "packages" / "geo"), str(HERE.parents[1] / "apps" / "api")]
import gazetteer, build_gazetteer as bg  # noqa: E402

conn = gazetteer.ensure()
conn.execute("UPDATE places SET osm_id='relation/1234' WHERE name='Kadıköy' AND level='ilce'")
did = conn.execute("SELECT id FROM places WHERE name='Kadıköy'").fetchone()[0]
assert "rel(1234)" in bg.query_district("relation/1234")
els = [{"type": "relation", "id": 1, "tags": {"name": "Moda Mahallesi", "admin_level": "9"}, "center": {"lat": 40.98, "lon": 29.03}},
       {"type": "relation", "id": 2, "tags": {"name": "Caferağa Mahallesi", "admin_level": "9"}, "center": {"lat": 40.99, "lon": 29.02}}]
assert bg.load_district(conn, did, 34, bg.parse(els)) == 2
assert bg.load_district(conn, did, 34, bg.parse(els)) == 0  # tekrar yazmaz
rows = conn.execute("SELECT name, district_id FROM places WHERE level='mahalle'").fetchall()
assert len(rows) == 2 and all(r[1] == did for r in rows), rows
assert conn.execute("SELECT COUNT(*) FROM loaded_mah").fetchone()[0] == 1
print("OK")
