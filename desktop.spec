# -*- mode: python ; coding: utf-8 -*-
# Build:  python -m PyInstaller --noconfirm --clean desktop.spec
# Hasil:  dist/EvaluasiPDRB/EvaluasiPDRB.exe  (mode onedir: start cepat, antivirus lebih tenang)
from PyInstaller.utils.hooks import collect_all, collect_submodules

datas = [("frontend/dist", "frontend/dist"), ("main.ipynb", ".")]
binaries = []
# Notebook dieksekusi lewat exec(), jadi import di dalamnya tidak terlihat oleh PyInstaller.
# Library yang dipakai notebook (pandas, openpyxl, dll.) harus disebut eksplisit.
hiddenimports = ["et_xmlfile", "multipart", "python_multipart"]
for pkg in ("webview", "openpyxl", "pandas"):
    d, b, h = collect_all(pkg)
    datas += d; binaries += b; hiddenimports += h
for pkg in ("uvicorn", "anyio", "starlette", "fastapi"):
    hiddenimports += collect_submodules(pkg)

a = Analysis(
    ["desktop.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["matplotlib", "scipy", "IPython", "pytest", "notebook", "jupyter"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="EvaluasiPDRB",
    console=False,            # tanpa jendela hitam; log ada di evaluasi_pdrb.log
    icon="assets/app.ico",
)
coll = COLLECT(exe, a.binaries, a.datas, name="EvaluasiPDRB")
