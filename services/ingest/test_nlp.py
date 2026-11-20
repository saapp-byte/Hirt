import tempfile
import unittest
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "geo"))
import gazetteer
from locate import Locator
from nlp import classify

def make_locator(extra=None):
    conn = gazetteer.ensure(Path(tempfile.mkdtemp()) / "p.db")
    for row in extra or []:
        conn.execute("INSERT INTO places(level,name,folded,province_id,district_id,lat,lng) VALUES (?,?,?,?,?,?,?)", row)
    conn.commit()
    return Locator(conn)

class ClassifyTests(unittest.TestCase):
    def test_kinds(self):
        self.assertEqual(classify("Kadıköy'de bıçaklı kavga: 2 yaralı"), "stabbing")
        self.assertEqual(classify("Ankara'da silahlı saldırı"), "assault")
        self.assertEqual(classify("Avcılar'da iki aile arasında kavga"), "fight")
    def test_excluded(self):
        self.assertIsNone(classify("İsrail'in Gazze'ye saldırısı sürüyor"))
        self.assertIsNone(classify("Galatasaray maçında kavga çıktı"))

class LocateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loc = make_locator([("mahalle", "Moda Mahallesi", "moda", 34, 1001, 40.98, 29.02)])

    def test_district_istanbul(self):
        r = self.loc.locate("Kadıköy'de bıçaklı kavga: 2 yaralı")
        self.assertEqual((r["province_id"], r["district_id"], r["precision"]), (34, 1001, "ilce"))
    def test_province_only(self):
        r = self.loc.locate("Ankara'da silahlı saldırı")
        self.assertEqual((r["province_id"], r["district_id"], r["precision"]), (6, None, "il"))
    def test_uppercase_dotted_i(self):
        self.assertEqual(self.loc.locate("ÜSKÜDAR'DA DARP EDİLDİ")["district_id"], 1002)
    def test_person_name_fatih(self):
        self.assertIsNone(self.loc.locate("Fatih Terim'e saldırı"))
    def test_ambiguous_district_needs_province(self):
        self.assertIsNone(self.loc.locate("Fatih'te silahlı saldırı"))
        self.assertEqual(self.loc.locate("İstanbul Fatih'te silahlı saldırı")["district_id"], 1006)
        self.assertEqual(self.loc.locate("Fatih'te kavga", hint=34)["district_id"], 1006)
    def test_ambiguous_province_needs_apostrophe(self):
        self.assertEqual(self.loc.locate("Van'da kavga")["province_id"], 65)
        self.assertIsNone(self.loc.locate("Van Gölü'nde kavga"))
        self.assertIsNone(self.loc.locate("Aydın Doğan'a saldırı"))
    def test_alias(self):
        self.assertEqual(self.loc.locate("Urfa'da kavga")["province_id"], 63)
    def test_neighborhood(self):
        r = self.loc.locate("Kadıköy Moda Mahallesi'nde bıçaklandı")
        self.assertEqual(r["precision"], "mahalle")
        self.assertEqual(r["label"], "Moda Mahallesi, Kadıköy, İstanbul")
    def test_destination_suffix_is_not_location(self):
        self.assertIsNone(self.loc.locate("Bıçaklanan şahıs Ankara'ya sevk edildi"))
        self.assertEqual(self.loc.locate("Ankara'da bıçaklanan genç hastaneye kaldırıldı")["province_id"], 6)
        self.assertIsNone(self.loc.locate("Yaralı Ankara'da hastaneye kaldırıldı"))
    def test_unknown_place(self):
        self.assertIsNone(self.loc.locate("Dünya'da kavga"))

if __name__ == "__main__":
    unittest.main()
