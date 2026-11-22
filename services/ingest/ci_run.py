"""GitHub Actions turu (ücretsiz): konum veritabanını zaman bütçesiyle tamamlar -> haberleri tarar -> statik JSON üretir.
Kullanım: HIRT_DATA_DIR=<kalıcı klasör> python services/ingest/ci_run.py <çıktı klasörü>"""
import os
import socket
import sys
import time
from argparse import Namespace
from pathlib import Path

# GitHub Actions makineleri IPv6'ya çıkamıyor ("Network is unreachable"): yalnızca IPv4 kullan.
_getaddrinfo = socket.getaddrinfo
def _ipv4_only(host, port, family=0, *a, **k):
    return _getaddrinfo(host, port, socket.AF_INET, *a, **k)
socket.getaddrinfo = _ipv4_only

HERE = Path(__file__).resolve().parent
sys.path += [str(HERE), str(HERE.parents[1] / "packages" / "geo"), str(HERE.parents[1] / "apps" / "api")]

import gazetteer  # noqa: E402
import jobs  # noqa: E402
from paths import DATA_DIR  # noqa: E402

def gazetteer_step(minutes):
    import build_gazetteer as bg
    deadline = time.time() + minutes * 60
    conn = gazetteer.ensure()
    done = {r[0] for r in conn.execute("SELECT province_id FROM loaded")}
    for plate in range(1, 82):
        if plate in done:
            continue
        if time.time() > deadline:
            print("[gazetteer] zaman bütçesi doldu; kalanlar sonraki turda.", flush=True)
            break
        try:
            data = bg.overpass(bg.query_for(plate))
            n = bg.load_province(conn, plate, bg.parse(data.get("elements", [])))
            print(f"[gazetteer] il {plate:02d}: ilçe {n[0]}, yeni mahalle {n[1]}", flush=True)
        except Exception as e:
            print(f"[gazetteer] il {plate:02d} başarısız: {str(e)[:80]}", flush=True)
        time.sleep(10)
    return conn.execute("SELECT COUNT(*) FROM loaded").fetchone()[0]

def finalize():
    """SQLite dosyalarını tek parça hâle getir (kalıcı branch'e kopyalanacak).
    Süreçte açık kalmış bağlantı varsa journal_mode değişmez ('database is locked'); o durumda
    VACUUM INTO ile bağımsız, tek dosyalık bir kopya üretip yerine koyarız."""
    import gc
    import sqlite3
    gc.collect()  # açık kalmış bağlantıları kapat
    for db in DATA_DIR.glob("*.db"):
        try:
            c = sqlite3.connect(db, timeout=60)
            c.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            c.execute("PRAGMA journal_mode=DELETE")
            c.close()
        except sqlite3.OperationalError as e:
            print(f"[finalize] {db.name}: {e}; VACUUM INTO ile kopyalanıyor", flush=True)
            tmp = db.with_name(db.name + ".tmp")
            tmp.unlink(missing_ok=True)
            c = sqlite3.connect(db, timeout=60)
            c.execute("VACUUM INTO ?", (str(tmp),))
            c.close()
            os.replace(tmp, db)
    for junk in list(DATA_DIR.glob("*-wal")) + list(DATA_DIR.glob("*-shm")):
        junk.unlink()

def main(out):
    import export_static
    import ingest
    st = jobs.read_status()
    first = not (DATA_DIR / "events.db").exists() or "last_gz" not in st
    gz = gazetteer_step(float(os.environ.get("GAZETTEER_MINUTES") or 40))
    reprocess = (not first) and gz > st.get("last_gz", -1)
    args = Namespace(days=30, quick=False, only="", no_google=False, no_direct=False, no_pages=False,
                     max_pages=int(os.environ.get("MAX_PAGES") or 150), reprocess=reprocess, dry_run=False, loop_hours=0)
    err = None
    try:
        ingest.run(args, 30 if (first or reprocess) else 3)
    except Exception as e:
        err = str(e)[:200]
        print("[ingest] hata:", err, flush=True)
    jobs.update_status(last_gz=gz, last_ingest={"error": err, "reprocessed": reprocess, "first": first})
    finalize()
    print("Üretilen özet dosyası:", export_static.export(out), flush=True)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "site")
