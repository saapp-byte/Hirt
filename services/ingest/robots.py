"""robots.txt'e uyma: sitenin izin vermediği sayfaları okumayız."""
import socket
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

AGENT = "HirtIptalBot"
_cache = {}

def allowed(url: str) -> bool:
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        return False
    rp = _cache.get(p.netloc)
    if rp is None:
        rp = RobotFileParser()
        rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
        old = socket.getdefaulttimeout()
        socket.setdefaulttimeout(10)
        try:
            rp.read()  # 404 -> serbest, 401/403 -> yasak
        except Exception:
            rp.disallow_all = True  # robots.txt okunamadıysa temkinli ol
        finally:
            socket.setdefaulttimeout(old)
        _cache[p.netloc] = rp
    return rp.can_fetch(AGENT, url)
