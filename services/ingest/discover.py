"""Kaynak keşfi: Google Haberler'de olay haberi yayımlayan sitelerin (özellikle yerel gazeteler) kendi RSS
adreslerini ana sayfalarındaki <link rel="alternate"> etiketinden bulur, doğrular ve kaydeder.
  python discover.py --limit 40"""
import argparse
import re
import time
import urllib.request
from urllib.parse import urljoin

import feeds
import robots
import sources
import store

LINK = re.compile(r"<link\b[^>]*>", re.I)

def find_feed_links(html, base):
    out = []
    for tag in LINK.findall(html):
        if re.search(r'rel\s*=\s*["\']?alternate', tag, re.I) and re.search(r'type\s*=\s*["\']?application/(rss|atom)\+xml', tag, re.I):
            m = re.search(r'href\s*=\s*["\']([^"\']+)["\']', tag, re.I)
            if m:
                out.append(urljoin(base, m.group(1)))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=40)
    a = ap.parse_args()
    conn = store.connect()
    known = {f["url"] for f in sources.all_feeds()}
    rows = conn.execute("SELECT name, url, n FROM outlets WHERE url IS NOT NULL AND url != '' ORDER BY n DESC LIMIT ?", (a.limit * 3,)).fetchall()
    done = 0
    for name, url, n in rows:
        if done >= a.limit:
            break
        done += 1
        if not robots.allowed(url):
            print(f"-  {name}: robots izin vermiyor")
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": feeds.UA})
            html = urllib.request.urlopen(req, timeout=15).read(800_000).decode("utf-8", "replace")
            for link in find_feed_links(html, url)[:3]:
                if link in known:
                    continue
                items = feeds.parse_feed(feeds.fetch(link, retries=1))
                if items:
                    sources.add_discovered({"name": name, "outlet": name, "url": link, "verified": True, "scope": "discovered"})
                    print(f"+  {name}: {link} ({len(items)} haber)")
                    break
        except Exception as e:
            print(f"!  {name}: {str(e)[:60]}")
        time.sleep(2)

if __name__ == "__main__":
    main()
