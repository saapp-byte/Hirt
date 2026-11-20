"""Her RSS kaynağını dener: çalışıyor mu, kaç haber, en yeni haber ne kadar eski? 
  python check_sources.py          # yalnızca rapor
  python check_sources.py --apply  # çalışmayanları devre dışı bırak"""
import sys
import time
from datetime import datetime, timezone

import feeds
import sources

def main():
    apply = "--apply" in sys.argv
    ok_n = 0
    for f in sources.all_feeds():
        try:
            items = feeds.parse_feed(feeds.fetch(f["url"], retries=1))
            if not items:
                raise ValueError("haber yok")
            newest = max(i["published"] for i in items)
            age_h = (datetime.now(timezone.utc) - newest).total_seconds() / 3600
            print(f"OK   {f['name']:<28} {len(items):>3} haber, en yeni {age_h:.1f} saat önce")
            ok_n += 1
            if apply:
                sources.record(f["url"], True)
        except Exception as e:
            print(f"HATA {f['name']:<28} {str(e)[:60]}  <- {f['url']}")
            if apply:
                sources.record(f["url"], False)
        time.sleep(1)
    print(f"{ok_n} kaynak çalışıyor.")

if __name__ == "__main__":
    main()
