"""Konum veritabanını kurar: il (yerleşik) + ilçe + mahalle (OpenStreetMap / Overpass API).

Kullanım:
  python build_gazetteer.py --province 34,06,35   # seçili iller (deneme için önerilir)
  python build_gazetteer.py --all                 # 81 il (uzun sürer; yarıda kesilirse kaldığı yerden devam eder)
  python build_gazetteer.py --stats               # veritabanında ne var göster

Veri © OpenStreetMap katkıcıları (ODbL). Uygulamada atıf gösterilmelidir.
Not: OSM'de Türkiye için mahalle/köy seviyeleri (8-10) tutarlı değildir; bu yüzden sonuç sayıları ekrana yazılır.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "geo"))
import gazetteer  # noqa: E402
from fold import fold  # noqa: E402

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
ENDPOINT = ENDPOINTS[0]
STRIP = {"mahallesi", "mahalle", "mah", "mh", "koyu", "koy", "ilcesi", "belediyesi"}
SKIP = {"merkez", "merkezi"}

def query_for(plate: int) -> str:
    # Varsayılan: yalnızca ilçeler (hafif, hızlı). Mahalleler için HIRT_MAHALLE=1 (ağır; sunucu zaman aşımına düşebilir).
    levels = "6|8|9|10" if os.environ.get("HIRT_MAHALLE") == "1" else "6"
    return (f'[out:json][timeout:120];\n'
            f'rel["boundary"="administrative"]["admin_level"="4"]["ISO3166-2"="TR-{plate:02d}"];\n'
            f'map_to_area->.a;\n'
            f'rel(area.a)["boundary"="administrative"]["admin_level"~"^({levels})$"];\n'
            f'out center tags;')

def overpass(q: str, retries: int = 4):
    delay = 30
    for attempt in range(retries + 1):
        endpoint = ENDPOINTS[attempt % len(ENDPOINTS)]  # her denemede sıradaki sunucuyu dene
        try:
            data = urllib.parse.urlencode({"data": q}).encode()
            req = urllib.request.Request(endpoint, data=data, headers={"User-Agent": "HirtIptal gazetteer"})
            with urllib.request.urlopen(req, timeout=150) as r:
                return json.loads(r.read())
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            code = getattr(e, "code", None)
            if attempt < retries and (code in (429, 502, 503, 504) or code is None):
                print(f"    bekleniyor ({code or e}), {delay} sn sonra yeniden...")
                time.sleep(delay)
                delay = min(delay * 2, 120)
                continue
            raise

def base_name(name: str) -> str:
    toks = fold(name).replace("'", " ").split()
    while toks and toks[-1] in STRIP:
        toks.pop()
    return " ".join(toks)

def parse(elements):
    """Overpass öğelerinden [{level, name, folded, lat, lng, osm_id}] çıkarır."""
    out = []
    for el in elements:
        tags, c = el.get("tags", {}), el.get("center")
        name, lvl = tags.get("name"), tags.get("admin_level")
        if not name or not c or lvl not in ("6", "8", "9", "10"):
            continue
        folded = base_name(name)
        if not folded or folded in SKIP:
            continue
        out.append({"level": "ilce" if lvl == "6" else "mahalle", "name": name.strip(), "folded": folded,
                    "lat": c["lat"], "lng": c["lon"], "osm_id": f"{el.get('type', 'relation')}/{el.get('id')}"})
    return out

def nearest(ilceler, lat, lng):
    return min(ilceler, key=lambda r: (r["lat"] - lat) ** 2 + (r["lng"] - lng) ** 2, default=None)

def load_province(conn, plate, parsed):
    """Bir ilin ilçe ve mahallelerini yazar. Mahalle -> en yakın ilçe merkezi (yaklaşık atama)."""
    existing = {r[0]: r[1] for r in conn.execute("SELECT folded, id FROM places WHERE level='ilce' AND province_id=?", (plate,))}
    for p in (x for x in parsed if x["level"] == "ilce"):
        if p["folded"] in existing:
            conn.execute("UPDATE places SET osm_id=? WHERE id=?", (p["osm_id"], existing[p["folded"]]))
            continue
        cur = conn.execute("INSERT INTO places(level,name,folded,province_id,lat,lng,osm_id) VALUES ('ilce',?,?,?,?,?,?)",
                           (p["name"], p["folded"], plate, p["lat"], p["lng"], p["osm_id"]))
        conn.execute("UPDATE places SET district_id=id WHERE id=?", (cur.lastrowid,))
        existing[p["folded"]] = cur.lastrowid
    ilceler = [dict(id=r[0], lat=r[1], lng=r[2]) for r in
               conn.execute("SELECT id, lat, lng FROM places WHERE level='ilce' AND province_id=?", (plate,))]
    n_mah = 0
    for p in (x for x in parsed if x["level"] == "mahalle"):
        if conn.execute("SELECT 1 FROM places WHERE osm_id=?", (p["osm_id"],)).fetchone():
            continue
        d = nearest(ilceler, p["lat"], p["lng"])
        conn.execute("INSERT INTO places(level,name,folded,province_id,district_id,lat,lng,osm_id) VALUES ('mahalle',?,?,?,?,?,?,?)",
                     (p["name"], p["folded"], plate, d["id"] if d else None, p["lat"], p["lng"], p["osm_id"]))
        n_mah += 1
    n_ilce = conn.execute("SELECT COUNT(*) FROM places WHERE level='ilce' AND province_id=?", (plate,)).fetchone()[0]
    conn.execute("INSERT OR REPLACE INTO loaded VALUES (?,?,?,?)", (plate, n_ilce, n_mah, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    return n_ilce, n_mah

def stats(conn):
    for lvl in ("il", "ilce", "mahalle"):
        print(f"  {lvl}: {conn.execute('SELECT COUNT(*) FROM places WHERE level=?', (lvl,)).fetchone()[0]}")
    done = conn.execute("SELECT COUNT(*) FROM loaded").fetchone()[0]
    print(f"  Overpass'tan yüklenen il: {done}/81")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--province", default="", help="plaka kodları, virgülle (34,06,35)")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    conn = gazetteer.ensure()
    if a.stats or not (a.province or a.all):
        print("Konum veritabanı:", gazetteer.DB_PATH)
        stats(conn)
        return
    plates = list(range(1, 82)) if a.all else [int(x) for x in a.province.split(",") if x.strip()]
    done = {r[0] for r in conn.execute("SELECT province_id FROM loaded")}
    todo = [p for p in plates if p not in done]
    print(f"{len(todo)} il yüklenecek ({len(plates) - len(todo)} zaten yüklü).")
    for i, plate in enumerate(todo, 1):
        name = conn.execute("SELECT name FROM places WHERE id=?", (plate,)).fetchone()[0]
        print(f"[{i}/{len(todo)}] {name} ({plate:02d}) indiriliyor...")
        try:
            data = overpass(query_for(plate))
            n_ilce, n_mah = load_province(conn, plate, parse(data.get("elements", [])))
            print(f"    ilçe: {n_ilce}, yeni mahalle: {n_mah}")
        except Exception as e:
            print(f"    ! {name} alınamadı: {e}")
        time.sleep(10)  # Overpass'a nazik davran
    stats(conn)

if __name__ == "__main__":
    main()
