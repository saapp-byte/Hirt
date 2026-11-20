"""Yayın sunucusu: API + /status + arka plan işleri (konum veritabanı tamamlama, düzenli haber tarama).
Çalıştır: python apps/api/server.py   (PORT ve HIRT_DATA_DIR ortam değişkenleri desteklenir)"""
import os
import sys
from http.server import ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path += [str(HERE), str(HERE.parents[1] / "services" / "ingest"), str(HERE.parents[1] / "packages" / "geo")]

import gazetteer  # noqa: E402
import jobs  # noqa: E402
import service  # noqa: E402
from dev_server import Handler  # noqa: E402

def status():
    conn = gazetteer.ensure()
    n = lambda lvl: conn.execute("SELECT COUNT(*) FROM places WHERE level=?", (lvl,)).fetchone()[0]
    events, sample = service._load()
    st = jobs.read_status()
    return {
        "ok": True,
        "gazetteer": {"il": n("il"), "ilce": n("ilce"), "mahalle": n("mahalle"),
                      "yuklenen_il": jobs.loaded_count(conn), "toplam_il": 81, "tamam": st.get("gazetteer_done", False)},
        "olaylar": {"toplam": len(events), "son_30_gun": len(service._recent(events)), "ornek_veri": sample},
        "son_tarama": st.get("last_ingest"),
    }

class H(Handler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            return self._send(200, {"ad": "Hırt İPTAL API", "durum": "/status", "bolgeler": "/areas"})
        if path == "/status":
            return self._send(200, status())
        return super().do_GET()

if __name__ == "__main__":
    jobs.start_background()
    port = int(os.environ.get("PORT", 8000))
    print(f"Sunucu: 0.0.0.0:{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
