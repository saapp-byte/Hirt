import unittest
from datetime import timezone
from urllib.robotparser import RobotFileParser

import articles
import feeds
import robots

LD = """<html><head><meta property="og:title" content="Kadıköy'de kavga">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"NewsArticle","headline":"Kadıköy'de kavga",
"datePublished":"2026-11-20T08:30:00+03:00","articleBody":"%s"}</script></head><body><p>Menü bağlantısı kısa</p></body></html>""" % ("Olay Moda Mahallesi'nde yaşandı. " * 10)
PLAIN = """<html><body><nav><p>Bu menü paragrafı atlanmalı çünkü nav içinde ve oldukça uzun bir metin</p></nav>
<script>var x = "<p>script içi</p>";</script>
<article><p>Kadıköy Moda Mahallesi'nde dün gece saat 02.30 sıralarında kavga çıktı, 1 kişi yaralandı.</p>
<p>Kısa.</p><p>Polis ekipleri olay yerine gelerek inceleme başlattı ve şüphelileri aradı.</p></article></body></html>"""
RSS = """<?xml version="1.0"?><rss version="2.0"><channel><item><title>Ankara'da kavga - Kaynak</title>
<link>https://ex.com/a</link><pubDate>Fri, 20 Nov 2026 06:00:00 +0000</pubDate><source url="https://kaynak.com">Kaynak</source>
<description>&lt;p&gt;Kavgada &lt;b&gt;1 kişi&lt;/b&gt; yaralandı&lt;/p&gt;</description></item></channel></rss>"""
ATOM = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry><title>İzmir'de saldırı</title>
<link rel="alternate" href="https://ex.com/b"/><updated>2026-11-20T09:00:00+03:00</updated><summary>Özet metni</summary></entry></feed>"""

class ArticleTests(unittest.TestCase):
    def test_json_ld(self):
        a = articles.extract_article(LD)
        self.assertIn("Moda Mahallesi", a["body"])
        self.assertEqual(a["published"].astimezone(timezone.utc).hour, 5)
    def test_plain_paragraphs(self):
        a = articles.extract_article(PLAIN)
        self.assertIn("Moda Mahallesi", a["body"]); self.assertIn("Polis ekipleri", a["body"])
        self.assertNotIn("menü paragrafı", a["body"]); self.assertNotIn("script içi", a["body"]); self.assertNotIn("Kısa.", a["body"])
    def test_robots(self):
        rp = RobotFileParser(); rp.parse(["User-agent: *", "Disallow: /private/"])
        robots._cache["ex.com"] = rp
        self.assertTrue(robots.allowed("https://ex.com/haber/1"))
        self.assertFalse(robots.allowed("https://ex.com/private/x"))
        self.assertFalse(robots.allowed("ftp://ex.com/x"))

class FeedTests(unittest.TestCase):
    def test_rss_description_and_source(self):
        it = feeds.parse_feed(RSS.encode())[0]
        self.assertEqual((it["title"], it["source"], it["source_url"]), ("Ankara'da kavga", "Kaynak", "https://kaynak.com"))
        self.assertEqual(it["description"], "Kavgada 1 kişi yaralandı")
    def test_atom(self):
        it = feeds.parse_feed(ATOM.encode())[0]
        self.assertEqual((it["link"], it["description"]), ("https://ex.com/b", "Özet metni"))
        self.assertEqual(it["published"].hour, 6)

if __name__ == "__main__":
    unittest.main()
