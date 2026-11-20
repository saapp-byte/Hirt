"""Başlıktan konum çıkarma: il > ilçe > mahalle. Belirsizse bir üst düzeyde kalır, asla tahmin etmez."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "geo"))
from fold import tokens  # noqa: E402

COLS = ("id", "level", "name", "folded", "province_id", "district_id", "lat", "lng", "ambiguous")
SKIP_NAMES = {"merkez", "merkezi"}

MOVE = {"a", "e", "ya", "ye", "na", "ne", "dan", "den", "tan", "ten", "ndan", "nden"}  # varış/ayrılış ekleri
HOSP = ("hastane", "sevk", "tedavi", "nakledil", "goturul", "kaldirildi")  # "Ankara'da hastaneye kaldırıldı"

def _match(base, suf, apos, name, ambiguous):
    """Ad eşleşmesi. None: eşleşmedi; aksi halde ek ('' = ek yok). Belirsiz adlar yalnızca apostrofla ek almışsa eşleşir."""
    if base == name:
        return None if (ambiguous and not apos) else suf
    if ambiguous or apos:
        return None
    if base.startswith(name) and 0 < len(base) - len(name) <= 4:
        return base[len(name):]
    return None

class Locator:
    def __init__(self, conn):
        self.places = {}
        self.prov_items = []   # (folded, satır)
        self.ilce_items = []   # (folded, [satırlar])
        self.mah_dist = {}     # ilçe_id -> {folded: satır}
        self.mah_prov = {}     # il_id -> {folded: [satırlar]}
        ilce = {}
        for r in conn.execute("SELECT %s FROM places" % ",".join(COLS)):
            row = dict(zip(COLS, r))
            self.places[row["id"]] = row
            if row["level"] == "il":
                self.prov_items.append((row["folded"], row))
            elif row["level"] == "ilce" and row["folded"] not in SKIP_NAMES:
                ilce.setdefault(row["folded"], []).append(row)
            elif row["level"] == "mahalle":
                if row["district_id"]:
                    self.mah_dist.setdefault(row["district_id"], {})[row["folded"]] = row
                self.mah_prov.setdefault(row["province_id"], {}).setdefault(row["folded"], []).append(row)
        for folded, pid in conn.execute("SELECT folded, place_id FROM aliases"):
            row = self.places.get(pid)
            if not row:
                continue
            if row["level"] == "il":
                self.prov_items.append((folded, row))
            elif row["level"] == "ilce":
                ilce.setdefault(folded, []).append(row)
        self.ilce_items = list(ilce.items())

    def locate(self, title, hint=None):
        toks = []
        for t in tokens(title):
            b, _, suf = t.partition("'")
            toks.append((b, "'" in t, suf))
        bases = [b for b, _, _ in toks]

        def eligible(i, suf):
            """Olay yeri sayılabilir mi? "Ankara'ya sevk edildi" ve "Ankara'da hastaneye kaldırıldı" olay yeri değildir."""
            if suf in MOVE:
                return False
            return not any(w.startswith(h) for w in bases[i + 1:i + 3] for h in HOSP)

        prov = None
        for i, (base, apos, suf) in enumerate(toks):
            for name, row in self.prov_items:
                s_ = _match(base, suf, apos, name, bool(row["ambiguous"]))
                if s_ is not None and eligible(i, s_):
                    prov = row
                    break
            if prov:
                break
        dist = None
        for i, (base, apos, suf) in enumerate(toks):
            for name, rows in self.ilce_items:
                amb = any(r["ambiguous"] for r in rows)
                s_ = _match(base, suf, apos, name, amb)
                if s_ is None or not eligible(i, s_):
                    continue
                ctx = prov["id"] if prov else None
                if ctx:
                    cands = [r for r in rows if r["province_id"] == ctx]
                elif len(rows) > 1 or amb:
                    cands = [r for r in rows if r["province_id"] == hint] if hint else []
                else:
                    cands = rows
                if len(cands) == 1:
                    dist = cands[0]
                    break
            if dist:
                break
        if dist and not prov:
            prov = self.places[dist["province_id"]]
        if not prov:
            return None
        neigh = None
        words = bases
        for i, w in enumerate(words):
            if not (w.startswith("mahalle") or w in ("mah", "mh")):
                continue
            for n in (3, 2, 1):
                if i - n < 0:
                    continue
                name = " ".join(words[i - n:i])
                if dist:
                    row = self.mah_dist.get(dist["id"], {}).get(name)
                else:
                    rows = self.mah_prov.get(prov["id"], {}).get(name, [])
                    row = rows[0] if len(rows) == 1 else None
                if row:
                    neigh = row
                    break
            if neigh:
                break
        if neigh and not dist and neigh["district_id"]:
            dist = self.places.get(neigh["district_id"])
        best = neigh or dist or prov
        names = [x["name"] for x in (neigh, dist, prov) if x]
        return {
            "province_id": prov["id"], "district_id": dist["id"] if dist else None,
            "neighborhood_id": neigh["id"] if neigh else None,
            "lat": best["lat"], "lng": best["lng"],
            "precision": "mahalle" if neigh else "ilce" if dist else "il",
            "label": ", ".join(names),
        }
