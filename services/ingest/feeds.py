"""RSS/Atom indirme (429/5xx'te bekleyip yeniden dener) ve ayrıştırma. Yalnızca standart kütüphane."""
import html as _html
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import quote

MAX_BYTES = 2_000_000  # beklenmedik derecede büyük yanıtları reddet
UA = "Mozilla/5.0 (compatible; HirtIptalBot/0.1; +https://github.com/saapp-byte/Hirt)"

def google_news_url(query: str) -> str:
    return f"https://news.google.com/rss/search?q={quote(query)}&hl=tr&gl=TR&ceid=TR:tr"

def fetch(url: str, timeout: int = 20, retries: int = 4) -> bytes:
    delay = 5
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                raise ValueError("Yanıt çok büyük")
            return data
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = int(e.headers.get("Retry-After", 0) or 0) or delay
                time.sleep(min(wait, 120))
                delay *= 2
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < retries:
                time.sleep(delay)
                delay *= 2
                continue
            raise

def _ln(el):
    return el.tag.rsplit("}", 1)[-1] if isinstance(el.tag, str) else ""

def _kid(el, name):
    for c in el:
        if _ln(c) == name:
            return c
    return None

def _text(el, name):
    c = _kid(el, name)
    return (c.text or "").strip() if c is not None else ""

def _strip_html(s: str, limit: int = 600) -> str:
    s = re.sub(r"<[^>]+>", " ", _html.unescape(s or ""))
    return " ".join(_html.unescape(s).split())[:limit]

def _date(s):
    if not s:
        return None
    try:
        dt = parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(s.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def parse_feed(xml_bytes: bytes):
    """RSS 2.0 ve Atom. [{title, link, published(UTC), source, source_url, description}] döndürür."""
    out = []
    root = ET.fromstring(xml_bytes)
    for el in root.iter():
        name = _ln(el)
        if name not in ("item", "entry"):
            continue
        title = _strip_html(_text(el, "title"), 300)
        if name == "item":
            link = _text(el, "link")
            pub = _date(_text(el, "pubDate") or _text(el, "date"))
            src_el = _kid(el, "source")
            src = (src_el.text or "").strip() if src_el is not None else ""
            src_url = (src_el.get("url") or "") if src_el is not None else ""
            desc = _strip_html(_text(el, "description"))
        else:
            link = ""
            for c in el:
                if _ln(c) == "link" and c.get("rel", "alternate") == "alternate" and c.get("href"):
                    link = c.get("href")
                    break
            pub = _date(_text(el, "published") or _text(el, "updated"))
            src, src_url = "", ""
            desc = _strip_html(_text(el, "summary") or _text(el, "content"))
        if not title or not link or not pub:
            continue
        suffix = f" - {src}"
        if src and title.endswith(suffix):
            title = title[: -len(suffix)].strip()
        out.append({"title": title, "link": link, "published": pub, "source": src or "Haber",
                    "source_url": src_url, "description": desc})
    return out

parse_rss = parse_feed  # eski ad
