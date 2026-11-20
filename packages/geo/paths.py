"""Veri klasörü. Sunucuda HIRT_DATA_DIR (kalıcı disk) ile değiştirilir."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("HIRT_DATA_DIR") or ROOT / "services" / "ingest" / "data")
