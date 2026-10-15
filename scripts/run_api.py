"""Arranque desde la raiz con entorno aislado; no cargar secrets en frontend."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "apps" / "api"
ENV = API / ".env"
if ENV.is_file():
    for line in ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
os.chdir(API)
subprocess.check_call([sys.executable, "dev.py"])
