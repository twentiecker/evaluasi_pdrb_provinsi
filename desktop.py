"""Peluncur aplikasi desktop: menjalankan server FastAPI lokal + jendela native (pywebview).

Jalankan langsung:  python desktop.py     (setelah `npm run build` di folder frontend)
Dibungkus jadi .exe dengan PyInstaller (lihat desktop.spec).
"""
from __future__ import annotations

import logging
import multiprocessing
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

# Mode tanpa konsol (.exe windowed): stdout/stderr bernilai None dan bisa membuat library crash.
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

import uvicorn  # noqa: E402

import api  # noqa: E402
import service  # noqa: E402
from paths import OUTPUT_DIR, WORK_DIR  # noqa: E402

APP_TITLE = "Evaluasi PDRB Provinsi"
_window = None  # disimpan global (bukan di dalam class API) agar pywebview tidak menelusurinya


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_ready(url: str, timeout: float = 20.0) -> None:
    end = time.time() + timeout
    while time.time() < end:
        try:
            urllib.request.urlopen(url + "/api/health", timeout=1).read()
            return
        except Exception:
            time.sleep(0.15)
    raise RuntimeError("Server lokal tidak merespons.")


class DesktopApi:
    """Dipanggil dari JavaScript lewat window.pywebview.api.*"""

    def save_excel(self, job_id: str) -> dict:
        import webview

        job = service.JOBS.get(job_id)
        if not job or not job.output_path or not Path(job.output_path).exists():
            return {"ok": False, "error": "Hasil evaluasi tidak ditemukan."}
        dialog = webview.FileDialog.SAVE if hasattr(webview, "FileDialog") else webview.SAVE_DIALOG
        dest = _window.create_file_dialog(
            dialog,
            directory=str(Path.home() / "Documents"),
            save_filename=Path(job.output_path).name,
            file_types=("Excel (*.xlsx)",),
        )
        if not dest:
            return {"ok": False, "cancelled": True}
        dest = dest if isinstance(dest, str) else dest[0]
        shutil.copyfile(job.output_path, dest)
        return {"ok": True, "path": str(dest)}

    def open_output_folder(self) -> dict:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith("win"):
            os.startfile(str(OUTPUT_DIR))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(OUTPUT_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(OUTPUT_DIR)])
        return {"ok": True, "path": str(OUTPUT_DIR)}


def run_native_window(url: str) -> None:
    global _window
    import webview

    _window = webview.create_window(
        APP_TITLE, url, js_api=DesktopApi(), width=1360, height=860, min_size=(980, 640)
    )
    webview.start()


def run_fallback(url: str) -> None:
    """Dipakai bila WebView2/pywebview tidak tersedia: buka browser + jendela kecil untuk berhenti."""
    import tkinter as tk
    import webbrowser

    webbrowser.open(url)
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("380x140")
    tk.Label(root, text="Aplikasi berjalan di browser Anda.\nTutup jendela ini untuk menghentikan aplikasi.", pady=18).pack()
    tk.Button(root, text="Buka lagi di browser", command=lambda: webbrowser.open(url)).pack()
    root.mainloop()


def main() -> None:
    multiprocessing.freeze_support()
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=str(WORK_DIR / "evaluasi_pdrb.log"), level=logging.WARNING)

    port = free_port()
    url = f"http://127.0.0.1:{port}"
    server = uvicorn.Server(uvicorn.Config(api.app, host="127.0.0.1", port=port, log_config=None))
    threading.Thread(target=server.run, daemon=True).start()

    try:
        wait_ready(url)
        try:
            run_native_window(url)
        except Exception:
            logging.exception("Jendela native gagal, beralih ke browser")
            run_fallback(url)
    except Exception:
        logging.exception("Aplikasi gagal dimulai")
        raise
    finally:
        server.should_exit = True
        time.sleep(0.3)
        os._exit(0)  # pastikan thread evaluasi yang masih berjalan tidak menahan proses keluar


if __name__ == "__main__":
    main()
