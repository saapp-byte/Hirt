"""Veritabanından statik JSON üretir (GitHub Pages'te yayınlanır). API ile aynı veriyi verir.
  areas.json              81 il
  areas/{id}.json         bir ilin ilçeleri / bir ilçenin olay olan mahalleleri
  summary/{id}.json       bölge özeti (il, ilçe ve olay olan mahalleler)
  status.json             üretim zamanı ve sayılar"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path += [str(HERE), str(HERE.parents[1] / "packages" / "geo"), str(HERE.parents[1] / "apps" / "api")]

import gazetteer  # noqa: E402
import service  # noqa: E402

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

def export(out):
    out = Path(out)
    evs = service._load()
    service._load = lambda: evs  # tek sefer oku, binlerce özette tekrar okuma
    n_sum = 0
    provinces = service.get_areas()
    write(out / "areas.json", provinces)
    for p in provinces:
        write(out / "summary" / f"{p['id']}.json", service.get_summary(p["id"]))
        n_sum += 1
        districts = service.get_areas(p["id"])
        if districts:
            write(out / "areas" / f"{p['id']}.json", districts)
        for d in districts:
            write(out / "summary" / f"{d['id']}.json", service.get_summary(d["id"]))
            n_sum += 1
            hoods = service.get_areas(d["id"])  # yalnızca olay olan mahalleler
            if hoods:
                write(out / "areas" / f"{d['id']}.json", hoods)
                for h in hoods:
                    write(out / "summary" / f"{h['id']}.json", service.get_summary(h["id"]))
                    n_sum += 1
    conn = gazetteer.ensure()
    count = lambda lvl: conn.execute("SELECT COUNT(*) FROM places WHERE level=?", (lvl,)).fetchone()[0]
    events, sample = evs
    write(out / "status.json", {
        "olusturma": datetime.now(timezone.utc).isoformat(),
        "il": count("il"), "ilce": count("ilce"), "mahalle": count("mahalle"),
        "olay_son_30_gun": len(service._recent(events)), "ornek_veri": sample, "ozet_dosyasi": n_sum,
        "yuklenen_il": conn.execute("SELECT COUNT(*) FROM loaded").fetchone()[0],
    })
    (out / ".nojekyll").write_text("")
    return n_sum

if __name__ == "__main__":
    print("Üretilen özet:", export(sys.argv[1] if len(sys.argv) > 1 else "site"))
