"""Haber sayfasını (robots.txt'e uyarak) okur ve metnini çıkarır. Metin SAKLANMAZ; yalnızca bellekte analiz edilir."""
import json
import time
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlparse

import robots
from feeds import UA

MAX_PAGE = 1_500_000
MIN_GAP = 2.0      # aynı siteye iki istek arası en az bekleme (sn)
SKIP_TAGS = {"style", "nav", "footer", "aside", "header", "form", "noscript", "svg", "iframe"}
_last = {}

class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.in_p, self.in_ld = 0, False, False
        self.cur, self.paras, self.ld, self.meta = [], [], [], {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script":
            if (a.get("type") or "").lower() == "application/ld+json":
                self.in_ld = True
                self.ld.append("")
            else:
                self.skip += 1
        elif tag in SKIP_TAGS:
            self.skip += 1
        elif tag == "meta":
            key = a.get("property") or a.get("name")
            if key and a.get("content"):
                self.meta[key] = a["content"]
        elif tag == "p" and not self.skip:
            self.in_p, self.cur = True, []
        elif tag == "br" and self.in_p:
            self.cur.append(" ")

    def handle_endtag(self, tag):
        if tag == "script":
            if self.in_ld:
                self.in_ld = False
            else:
                self.skip = max(0, self.skip - 1)
        elif tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
        elif tag == "p" and self.in_p:
            txt = " ".join("".join(self.cur).split())
            self.in_p = False
            if len(txt) >= 40:
                self.paras.append(txt)

    def handle_data(self, d):
        if self.in_ld:
            self.ld[-1] += d
        elif self.in_p and not self.skip:
            self.cur.append(d)

def _iso(s):
    try:
        dt = datetime.fromisoformat(str(s).strip().replace("Z", "+00:00"))
        return (dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
    except ValueError:
        return None

def _ld_articles(blobs):
    for b in blobs:
        try:
            data = json.loads(b)
        except ValueError:
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                if "@graph" in o:
                    stack += o["@graph"] if isinstance(o["@graph"], list) else [o["@graph"]]
                t = o.get("@type")
                t = " ".join(t) if isinstance(t, list) else str(t or "")
                if "Article" in t:
                    yield o

def extract_article(html: str, max_chars: int = 8000):
    """{headline, published(UTC|None), body}. Önce JSON-LD (NewsArticle), olmazsa <p> paragrafları."""
    p = _Page()
    try:
        p.feed(html)
    except Exception:
        pass
    headline, published, body = p.meta.get("og:title", ""), _iso(p.meta.get("article:published_time")), ""
    for art in _ld_articles(p.ld):
        headline = art.get("headline") or headline
        published = _iso(art.get("datePublished")) or published
        if len(str(art.get("articleBody") or "")) >= 200:
            body = str(art["articleBody"])
            break
    if not body:
        body = " ".join(p.paras)
    return {"headline": headline.strip(), "published": published, "body": " ".join(body.split())[:max_chars]}

def read(url: str, timeout: int = 15):
    """Sayfayı indirip çıkarır. robots.txt izin vermezse veya hata olursa None."""
    host = urlparse(url).netloc
    if not robots.allowed(url):
        return None
    wait = MIN_GAP - (time.time() - _last.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last[host] = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(MAX_PAGE + 1)
            charset = r.headers.get_content_charset() or "utf-8"
        if len(raw) > MAX_PAGE:
            return None
        art = extract_article(raw.decode(charset, errors="replace"))
        return art if art["body"] else None
    except Exception:
        return None
