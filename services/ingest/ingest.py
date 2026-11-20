"""Haber toplama (Türkiye geneli).
Kaynaklar: (A) doğrudan RSS/Atom kaynakları (sources.json + keşfedilenler) -> sayfa içi okuma (robots.txt'e uyarak)
           (B) Google Haberler RSS arama sorguları (yalnızca başlık; keşif ve tamamlayıcı)
Olay türü + konum (il/ilçe/mahalle) + saat + sokak çıkarılır, aynı olaylar birleştirilir, SQLite'a yazılır.
Haber METNİ saklanmaz; yalnızca çıkarılan bilgi, başlık ve bağlantı tutulur.

Kullanım:
  python ingest.py                          # son 30 gün, tüm kaynaklar, 81 il
  python ingest.py --only Ankara,İzmir      # seçili iller (Google sorguları)
  python ingest.py --quick                  # Google'da yalnızca genel sorgular
  python ingest.py --no-google              # yalnızca doğrudan kaynaklar (hızlı, günlük için ideal)
  python ingest.py --loop-hours 6           # her 6 saatte bir kendini tekrarlar (ilk tur 30 gün, sonrakiler 3 gün)
  python ingest.py --dry-run                # kaydetmeden göster
  python ingest.py --reprocess              # daha önce görülen haberleri de yeniden işle
"""
import argparse
import hashlib
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "geo"))
import gazetteer  # noqa: E402
from fold import fold  # noqa: E402

import articles  # noqa: E402
import extract  # noqa: E402
import feeds  # noqa: E402
import sources  # noqa: E402
import store  # noqa: E402
from cluster import compatible, merge_place  # noqa: E402
from locate import Locator  # noqa: E402
from nlp import classify_item  # noqa: E402

GENERIC = ["bıçaklandı", "bıçaklı saldırı", "silahlı saldırı", "kavga", "darp edildi", "saldırıya uğradı"]
KINDS = ["bıçaklandı", "silahlı saldırı", "kavga"]
CLUSTER_HOURS = 72
PAUSE = 2.0

def pick_provinces(conn, only):
    rows = conn.execute("SELECT id, name, folded FROM places WHERE level='il' ORDER BY id").fetchall()
    if not only:
        return rows
    wanted = [x.strip() for x in only.split(",") if x.strip()]
    out = [r for r in rows if str(r[0]) in wanted or r[2] in {fold(w) for w in wanted}]
    if not out:
        sys.exit(f"Eşleşen il bulunamadı: {only}")
    return out

def build_queries(days, provinces, quick, conn):
    """[(sorgu, il_ipucu)]"""
    out = [(f"{q} when:{days}d", None) for q in GENERIC]
    if quick:
        return out
    for pid, name, _ in provinces:
        out += [(f"{name} {k} when:{days}d", pid) for k in KINDS]
    return out

def choose_loc(locator, title, lead, hint):
    """Başlık ve gövde başından konum: çelişirse başlığa güven."""
    lt = locator.locate(title, hint=hint)
    ll = locator.locate(lead, hint=hint)
    if lt and ll and not compatible(lt, ll):
        return lt
    return ll or lt

def process(items, since, locator, page_fn=None):
    """Haberleri olaylara dönüştürür. Dönen: ([olay], sayaçlar, [işlenen bağlantılar])."""
    events, stats, clusters, done = [], Counter(), {}, []
    for it in sorted(items, key=lambda x: x["published"]):
        if it["published"] < since:
            stats["eski"] += 1
            continue
        title = it["title"]
        desc = it.get("description") if it.get("direct") else ""
        kind = classify_item(title, desc or "")
        if not kind:
            stats["olay_degil"] += 1
            continue
        done.append(it["link"])
        if extract.stale_reason(f"{title} {desc or ''}", it["published"]):
            stats["eski_olay"] += 1
            continue
        body = ""
        if page_fn and it.get("direct"):
            pg = page_fn(it["link"])
            if pg:
                body = pg["body"]
                stats["sayfa_okundu"] += 1
                if extract.stale_reason(body[:1200], it["published"]):
                    stats["eski_olay"] += 1
                    continue
        lead = " ".join(x for x in (title, desc, body[:1500]) if x)
        loc = choose_loc(locator, title, lead, it.get("hint"))
        if not loc:
            stats["konum_yok"] += 1
            continue
        info = extract.analyze(lead, it["published"])
        occ = info["occurred_at"]
        lst = clusters.setdefault((kind, loc["province_id"]), [])
        ev = next((e for e in lst if abs(occ - e["_start"]) <= timedelta(hours=CLUSTER_HOURS) and compatible(e, loc)), None)
        if ev is None:
            eid = hashlib.sha1(f"{kind}|{loc['province_id']}|{occ.isoformat()}|{len(events)}".encode()).hexdigest()[:16]
            ev = {"id": eid, "kind": kind, "occurred_at": occ.isoformat(), "time_precision": info["time_precision"],
                  "street": info["street"], "outcome": info["outcome"], "sources": [], "_start": occ,
                  **{k: loc[k] for k in ("province_id", "district_id", "neighborhood_id", "lat", "lng", "precision", "label")}}
            lst.append(ev)
            events.append(ev)
        else:
            merge_place(ev, loc)
            ev["occurred_at"], ev["time_precision"] = store.best_time(ev["occurred_at"], ev["time_precision"],
                                                                      occ.isoformat(), info["time_precision"])
            ev["street"] = ev["street"] or info["street"]
            if store.SEV[info["outcome"]] > store.SEV[ev["outcome"]]:
                ev["outcome"] = info["outcome"]
        src = {"name": it["source"], "url": it["link"], "title": title}
        if all(x["url"] != src["url"] for x in ev["sources"]):
            ev["sources"].append(src)
        stats["kabul"] += 1
    for ev in events:
        ev.pop("_start", None)
    return events, stats, done

def collect_direct(since):
    items = []
    for f in sources.load():
        try:
            got = [it for it in feeds.parse_feed(feeds.fetch(f["url"], retries=2)) if it["published"] >= since]
            for it in got:
                it.update(hint=None, direct=True, source=f.get("outlet") or f["name"])
            items += got
            sources.record(f["url"], True)
            print(f"  {f['name']}: {len(got)} haber")
        except Exception as e:
            sources.record(f["url"], False)
            print(f"  ! {f['name']} alınamadı: {str(e)[:60]}")
        time.sleep(1)
    return items

def collect_google(queries, conn):
    items, seen = [], set()
    for n, (q, hint) in enumerate(queries, 1):
        if n % 20 == 0:
            print(f"  {n}/{len(queries)}")
        try:
            for it in feeds.parse_feed(feeds.fetch(feeds.google_news_url(q))):
                if it["link"] not in seen:
                    seen.add(it["link"])
                    it.update(hint=hint, direct=False, description="")
                    items.append(it)
                    if it["source"] and it["source_url"]:
                        store.add_outlet(conn, it["source"], it["source_url"])
        except Exception as e:
            print(f"  ! '{q}' alınamadı: {str(e)[:60]}")
        time.sleep(PAUSE)
    conn.commit()
    return items

def make_page_fn(max_pages):
    budget = [max_pages]
    def fn(url):
        if budget[0] <= 0:
            return None
        budget[0] -= 1
        return articles.read(url)
    return fn

def run(a, days):
    gconn = gazetteer.ensure()
    locator = Locator(gconn)
    conn = store.connect()
    since = datetime.now(timezone.utc) - timedelta(days=days)
    items = []
    if not a.no_direct:
        print("Doğrudan kaynaklar taranıyor...")
        items += collect_direct(since)
    if not a.no_google:
        provinces = pick_provinces(gconn, a.only)
        queries = build_queries(days, provinces, a.quick, gconn)
        print(f"Google Haberler: {len(queries)} sorgu...")
        items += collect_google(queries, conn)
    seen = set() if a.reprocess else store.seen_urls(conn)
    fresh = [it for it in items if it["link"] not in seen]
    page_fn = None if a.no_pages else make_page_fn(a.max_pages)
    events, stats, done = process(fresh, since, locator, page_fn)
    by_prec = Counter(e["precision"] for e in events)
    by_time = Counter(e["time_precision"] or "yok" for e in events)
    print(f"Toplanan: {len(items)} | yeni: {len(fresh)} | {dict(stats)}")
    print(f"Bulunan olay: {len(events)} | konum: {dict(by_prec)} | saat: {dict(by_time)}")
    for e in sorted(events, key=lambda x: x["occurred_at"], reverse=True)[:10]:
        st = f" · {e['street']}" if e["street"] else ""
        print(f"  - {e['occurred_at'][:16]} {e['label'][:34]}{st} [{e['kind']}, {len(e['sources'])} kaynak]")
    if a.dry_run:
        print("(dry-run: kaydedilmedi)")
        return
    for e in events:
        store.upsert(conn, e)
    store.mark_seen(conn, done)
    print(f"Kaydedildi: {store.DB_PATH}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--quick", action="store_true", help="Google'da yalnızca genel sorgular")
    ap.add_argument("--only", default="", help="Google sorguları için virgülle il adı/plaka")
    ap.add_argument("--no-google", action="store_true")
    ap.add_argument("--no-direct", action="store_true")
    ap.add_argument("--no-pages", action="store_true", help="haber sayfalarını okuma")
    ap.add_argument("--max-pages", type=int, default=150, help="tur başına en fazla sayfa")
    ap.add_argument("--reprocess", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--loop-hours", type=float, default=0)
    a = ap.parse_args()
    first = True
    while True:
        run(a, a.days if first else min(a.days, 3))
        first = False
        if not a.loop_hours:
            break
        print(f"{a.loop_hours} saat sonra tekrar çalışacak (durdurmak için Ctrl+C)...")
        time.sleep(a.loop_hours * 3600)

if __name__ == "__main__":
    main()
