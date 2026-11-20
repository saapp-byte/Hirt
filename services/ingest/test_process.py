import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import store
from ingest import process
from test_nlp import make_locator

NOW = datetime(2026, 11, 19, 12, tzinfo=timezone.utc)

def item(title, days_ago, n):
    return {"title": title, "link": f"https://ex.com/{n}", "published": NOW - timedelta(days=days_ago), "source": f"Kaynak{n}"}

class ProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loc = make_locator()

    def run_p(self, items):
        ev, st, _ = process(items, NOW - timedelta(days=30), self.loc)
        return ev, st

    def test_same_event_across_days_is_one(self):
        ev, _ = self.run_p([item("Eyüpsultan'da silahlı saldırı", 3, 1), item("Eyüpsultan'daki silahlı saldırıda yeni gelişme", 2, 2),
                            item("Eyüpsultan'da silahlı saldırı sonrası gözaltı", 1, 3)])
        self.assertEqual(len(ev), 1); self.assertEqual(len(ev[0]["sources"]), 3)

    def test_distant_events_stay_separate(self):
        ev, _ = self.run_p([item("Esenyurt'ta kavga", 6, 1), item("Esenyurt'ta kavga çıktı", 1, 2)])
        self.assertEqual(len(ev), 2)

    def test_province_and_district_merge_keep_precision(self):
        ev, _ = self.run_p([item("İstanbul'da silahlı saldırı", 2, 1), item("Kadıköy'de silahlı saldırı", 2, 2)])
        self.assertEqual(len(ev), 1); self.assertEqual(ev[0]["precision"], "ilce")

    def test_different_districts_do_not_merge(self):
        ev, _ = self.run_p([item("Kadıköy'de kavga", 2, 1), item("Üsküdar'da kavga", 2, 2)])
        self.assertEqual(len(ev), 2)

    def test_other_cities_work(self):
        ev, st = self.run_p([item("Ankara'da bıçaklı saldırı", 1, 1), item("İzmir'de kavga", 1, 2), item("Dünya'da kavga", 1, 3)])
        self.assertEqual({e["province_id"] for e in ev}, {6, 35}); self.assertEqual(st["konum_yok"], 1)

    def test_store_merges_across_runs(self):
        c = store.connect(Path(tempfile.mkdtemp()) / "e.db")
        for days_ago, n, t in [(3, 1, "Maltepe'de taksi durağına silahlı saldırı"), (1, 2, "İstanbul'da taksi durağına silahlı saldırı")]:
            ev, _ = self.run_p([item(t, days_ago, n)])
            for e in ev:
                store.upsert(c, e)
        self.assertEqual(c.execute("SELECT COUNT(*) FROM events").fetchone()[0], 1)
        self.assertEqual(c.execute("SELECT precision FROM events").fetchone()[0], "ilce")

class PageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loc = make_locator([("mahalle", "Moda Mahallesi", "moda", 34, 1001, 40.98, 29.02)])

    def direct(self, title, n=1, days_ago=0):
        d = item(title, days_ago, n); d["direct"] = True; d["description"] = ""
        return d

    def test_body_gives_neighborhood_time_street(self):
        body = "Dün gece saat 02.30 sıralarında Kadıköy Moda Mahallesi Bahariye Caddesi'nde çıkan kavgada 1 kişi yaralandı."
        ev, st, _ = process([self.direct("Bıçaklı kavga: 1 yaralı")], NOW - timedelta(days=30), self.loc, lambda u: {"body": body})
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["precision"], e["time_precision"], e["street"], e["outcome"]), ("mahalle", "dakika", "Bahariye Caddesi", "injured"))
        self.assertEqual(st["sayfa_okundu"], 1)

    def test_old_crime_news_is_dropped(self):
        ev, st, _ = process([self.direct("Iğdır'da 4 yıldır aranan silahlı saldırı şüphelisi yakalandı")], NOW - timedelta(days=30), self.loc)
        self.assertEqual((len(ev), st["eski_olay"]), (0, 1))

    def test_hospital_city_is_not_incident_place(self):
        ev, st, _ = process([self.direct("İnebolu'da bıçaklanan şahıs Ankara'ya sevk edildi")], NOW - timedelta(days=30), self.loc)
        self.assertEqual(len(ev), 0)

    def test_google_items_never_fetch_pages(self):
        called = []
        g = item("Kadıköy'de kavga", 1, 9)
        process([g], NOW - timedelta(days=30), self.loc, lambda u: called.append(u))
        self.assertEqual(called, [])

if __name__ == "__main__":
    unittest.main()
