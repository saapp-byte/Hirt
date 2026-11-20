"""APK derlemesi için app.json'u hazırlar (ad, paket adı). Kullanım: python prepare_build.py"""
import json
from pathlib import Path

p = Path(__file__).with_name("app.json")
cfg = json.loads(p.read_text(encoding="utf-8"))
e = cfg.setdefault("expo", {})
e["name"] = e.get("name") or "Hırt İPTAL"
e.setdefault("slug", "hirt-iptal")
e.setdefault("version", "0.1.0")
e.setdefault("android", {})["package"] = e["android"].get("package") or "com.saappbyte.hirt"
p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
print("app.json hazır:", e["android"]["package"])
