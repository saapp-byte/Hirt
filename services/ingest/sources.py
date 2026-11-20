"""Doğrudan RSS kaynakları: yerleşik liste + keşfedilenler. Üst üste 5 kez başarısız olan kaynak devre dışı kalır."""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "packages" / "geo"))
from paths import DATA_DIR  # noqa: E402

HERE = Path(__file__).resolve().parent
BUILTIN = HERE / "sources.json"
DATA = DATA_DIR
DISCOVERED = DATA / "sources_discovered.json"
STATE = DATA / "sources_state.json"
MAX_FAILS = 5

def _read(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default

def all_feeds():
    return _read(BUILTIN, {"feeds": []})["feeds"] + _read(DISCOVERED, {"feeds": []})["feeds"]

def load():
    state = _read(STATE, {})
    return [f for f in all_feeds() if not state.get(f["url"], {}).get("disabled")]

def record(url, ok):
    DATA.mkdir(parents=True, exist_ok=True)
    state = _read(STATE, {})
    s = state.setdefault(url, {"fails": 0})
    s["fails"] = 0 if ok else s["fails"] + 1
    s["disabled"] = s["fails"] >= MAX_FAILS
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")

def add_discovered(feed):
    DATA.mkdir(parents=True, exist_ok=True)
    cur = _read(DISCOVERED, {"feeds": []})
    if all(f["url"] != feed["url"] for f in cur["feeds"]):
        cur["feeds"].append(feed)
        DISCOVERED.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
