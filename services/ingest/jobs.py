"""Sunucuda arka plan işleri: (1) 81 ilin ilçe/mahalle verisini tamamlar, (2) haberleri düzenli tarar."""
import json
import os
import sys
import threading
import time
import traceback
from argparse import Namespace
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "geo"))
import gazetteer  # noqa: E402
from paths import DATA_DIR  # noqa: E402

STATUS = DATA_DIR / "status.json"
_lock = threading.Lock()

def update_status(**kw):
    with _lock:
        cur = read_status()
        cur.update(kw)
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        STATUS.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")

def read_status():
    try:
        return json.loads(STATUS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}

def loaded_count(conn):
    return conn.execute("SELECT COUNT(*) FROM loaded").fetchone()[0]

def gazetteer_job(max_attempts=3):
    """Eksik illeri sırayla indirir (kesilirse kaldığı yerden devam eder). Bir il 3 kez başarısız olursa atlanır."""
    import build_gazetteer as bg
    attempts = {}
    while True:
        conn = gazetteer.ensure()
        done = {r[0] for r in conn.execute("SELECT province_id FROM loaded")}
        todo = [p for p in range(1, 82) if p not in done and attempts.get(p, 0) < max_attempts]
        update_status(gazetteer_loaded=len(done), gazetteer_total=81)
        if not todo:
            update_status(gazetteer_done=True)
            return
        for plate in todo:
            try:
                data = bg.overpass(bg.query_for(plate))
                bg.load_province(conn, plate, bg.parse(data.get("elements", [])))
                print(f"[gazetteer] il {plate:02d} tamam", flush=True)
            except Exception as e:
                attempts[plate] = attempts.get(plate, 0) + 1
                print(f"[gazetteer] il {plate:02d} başarısız ({attempts[plate]}/{max_attempts}): {str(e)[:80]}", flush=True)
            time.sleep(10)  # Overpass'a nazik davran
        time.sleep(60)

def ingest_once(first, last_gz):
    import ingest
    conn = gazetteer.ensure()
    gz = loaded_count(conn)
    reprocess = (not first) and gz > last_gz  # yeni iller geldiyse eski haberleri de yeniden değerlendir
    args = Namespace(days=30, quick=False, only="", no_google=False, no_direct=False, no_pages=False,
                     max_pages=150, reprocess=reprocess, dry_run=False, loop_hours=0)
    started = datetime.now(timezone.utc).isoformat()
    err = None
    try:
        ingest.run(args, 30 if (first or reprocess) else 3)
    except Exception as e:  # tek tur başarısız olsa da sunucu çalışmaya devam eder
        err = str(e)[:200]
        traceback.print_exc()
    update_status(last_ingest={"started": started, "finished": datetime.now(timezone.utc).isoformat(), "error": err,
                               "reprocessed": reprocess})
    return gz

def ingest_job(every_hours):
    first, last_gz = True, -1
    while True:
        last_gz = ingest_once(first, last_gz)
        first = False
        time.sleep(every_hours * 3600)

def start_background():
    if os.environ.get("HIRT_NO_JOBS") == "1":
        return
    hours = float(os.environ.get("INGEST_EVERY_HOURS") or 3)
    for fn, args in ((gazetteer_job, ()), (ingest_job, (hours,))):
        threading.Thread(target=fn, args=args, daemon=True).start()
