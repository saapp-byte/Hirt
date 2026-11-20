import tempfile
import unittest
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "geo"))
import gazetteer
import build_gazetteer as bg

def el(id_, name, lvl, lat, lon):
    return {"type": "relation", "id": id_, "tags": {"name": name, "admin_level": lvl}, "center": {"lat": lat, "lon": lon}}

class BuilderTests(unittest.TestCase):
    def test_parse_and_load(self):
        elements = [el(1, "Mamak", "6", 39.93, 32.92), el(2, "Çankaya", "6", 39.90, 32.86),
                    el(3, "Cebeci Mahallesi", "9", 39.94, 32.90), el(4, "Kızılay Mahallesi", "10", 39.92, 32.85),
                    el(5, "Merkez", "6", 39.9, 32.8), {"type": "relation", "id": 6, "tags": {"name": "X", "admin_level": "8"}}]
        parsed = bg.parse(elements)
        self.assertEqual(len(parsed), 4)
        self.assertEqual(next(p for p in parsed if p["name"].startswith("Cebeci"))["folded"], "cebeci")
        conn = gazetteer.ensure(Path(tempfile.mkdtemp()) / "p.db")
        n_ilce, n_mah = bg.load_province(conn, 6, parsed)
        self.assertEqual((n_ilce, n_mah), (2, 2))
        d = conn.execute("SELECT p.name FROM places m JOIN places p ON p.id=m.district_id WHERE m.folded='cebeci'").fetchone()[0]
        self.assertEqual(d, "Mamak")  # en yakın ilçe merkezi
        self.assertEqual(bg.load_province(conn, 6, parsed)[1], 0)  # ikinci yükleme tekrar eklemez

if __name__ == "__main__":
    unittest.main()
