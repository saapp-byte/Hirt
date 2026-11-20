import unittest
from datetime import datetime, timedelta, timezone

import extract

PUB = datetime(2026, 11, 20, 6, 0, tzinfo=timezone.utc)  # 09:00 TR
def tr(dt): return (dt + extract.TR).strftime("%m-%d %H:%M")

class ExtractTests(unittest.TestCase):
    def test_last_night_clock(self):
        r = extract.analyze("Dün gece saat 02.30 sıralarında kavga çıktı", PUB)
        self.assertEqual((tr(r["occurred_at"]), r["time_precision"]), ("11-20 02:30", "dakika"))
    def test_evening_clock_goes_to_previous_day(self):
        r = extract.analyze("Akşam saat 21.15'te silahlı saldırı", PUB)
        self.assertEqual(tr(r["occurred_at"]), "11-19 21:15")
    def test_part_of_day(self):
        r = extract.analyze("Bu sabah kavga çıktı", PUB)
        self.assertEqual((tr(r["occurred_at"]), r["time_precision"]), ("11-20 08:00", "dilim"))
    def test_no_time_falls_back_to_publish(self):
        r = extract.analyze("Bıçaklı saldırı: 1 yaralı", PUB)
        self.assertEqual((r["occurred_at"], r["time_precision"]), (PUB, None))
    def test_yesterday_day_only(self):
        r = extract.analyze("Dün kavga çıktı", PUB)
        self.assertEqual((r["time_precision"], tr(r["occurred_at"])[:5]), ("gun", "11-19"))
    def test_stale(self):
        self.assertTrue(extract.stale_reason("Iğdır'da 4 yıldır aranan şüpheli yakalandı", PUB))
        self.assertTrue(extract.stale_reason("Bıçaklı saldırı davasında karar çıktı: hapis cezası", PUB))
        self.assertTrue(extract.stale_reason("2019 yılında yaşanan saldırı", PUB))
        self.assertIsNone(extract.stale_reason("Kadıköy'de bıçaklı kavga", PUB))
    def test_street(self):
        self.assertEqual(extract.analyze("Olay Atatürk Caddesi'nde yaşandı", PUB)["street"], "Atatürk Caddesi")
        self.assertIsNone(extract.analyze("Caddede kavga çıktı", PUB)["street"])
    def test_outcome(self):
        self.assertEqual(extract.analyze("Kavgada 1 kişi hayatını kaybetti", PUB)["outcome"], "died")
        self.assertEqual(extract.analyze("Bıçaklanan genç yaralandı", PUB)["outcome"], "injured")

if __name__ == "__main__":
    unittest.main()
