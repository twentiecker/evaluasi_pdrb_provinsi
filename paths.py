"""Lokasi file untuk mode biasa (python) maupun hasil build .exe (PyInstaller)."""
from __future__ import annotations

import sys
from pathlib import Path

FROZEN = bool(getattr(sys, "frozen", False))

if FROZEN:
    APP_DIR = Path(sys.executable).resolve().parent            # folder tempat .exe berada
    BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", APP_DIR))       # file yang dibundel PyInstaller
else:
    APP_DIR = BUNDLE_DIR = Path(__file__).resolve().parent


def _writable(folder: Path) -> bool:
    try:
        folder.mkdir(parents=True, exist_ok=True)
        probe = folder / ".write_test"
        probe.write_text("x")
        probe.unlink()
        return True
    except OSError:
        return False


# Folder kerja: hasil evaluasi ditulis ke <WORK_DIR>/data/output.
# Jika folder .exe tidak bisa ditulis (mis. Program Files), pakai Documents.
WORK_DIR = APP_DIR if (not FROZEN or _writable(APP_DIR)) else Path.home() / "Documents" / "Evaluasi PDRB"
OUTPUT_DIR = WORK_DIR / "data" / "output"


def _find_notebook() -> Path:
    # main.ipynb di samping .exe diutamakan agar threshold bisa diubah pengguna.
    for candidate in (APP_DIR / "main.ipynb", BUNDLE_DIR / "main.ipynb"):
        if candidate.exists():
            return candidate
    return APP_DIR / "main.ipynb"


NOTEBOOK_PATH = _find_notebook()
DIST_DIR = BUNDLE_DIR / "frontend" / "dist"
