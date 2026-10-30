"""Lapisan layanan (tanpa dependensi web): upload, antrian job, query hasil.

api.py hanya membungkus fungsi-fungsi di sini menjadi endpoint FastAPI.
"""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd

import engine

from paths import NOTEBOOK_PATH, WORK_DIR

MAX_UPLOAD_BYTES = 100 * 1024 * 1024

# Nama kolom Excel yang panjang/aneh dipendekkan untuk API (file Excel tidak berubah).
API_COLUMNS = {
    "No": "no",
    "Kabkot": "kabkot",
    "Komponen": "komponen",
    "Periode": "periode",
    "Indikator ((qtq/yoy/ctc/SoG/implisit/share/dst...))": "indikator",
    "Nilai": "nilai",
    "Evaluasi": "evaluasi",
    "Keterangan": "keterangan",
    "Respon Daerah": "respon",
}


@dataclass
class Upload:
    id: str
    filename: str
    path: Path
    sheets: list[str]
    missing: list[str]
    periods: list[str]


@dataclass
class Job:
    id: str
    upload_id: str
    periode: str
    source: str
    status: str = "queued"          # queued | running | done | error
    current: int = 0
    total: int = 0
    error: str | None = None
    created: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    df: pd.DataFrame | None = None
    output_path: Path | None = None


UPLOADS: dict[str, Upload] = {}
JOBS: dict[str, Job] = {}
# Satu worker: engine memakai os.chdir() yang bersifat global per proses,
# jadi evaluasi dijalankan satu per satu (yang lain mengantre).
_EXECUTOR = ThreadPoolExecutor(max_workers=1)
_LOCK = threading.Lock()


def kategori_evaluasi(text: str) -> str:
    t = str(text)
    if re.match(r"^(Pertumbuhan )?[Tt]ertinggi", t):
        return "Peringkat pertumbuhan tertinggi sepulau"
    if re.match(r"^(Pertumbuhan )?[Tt]erendah", t):
        return "Peringkat pertumbuhan terendah sepulau"
    return t


# ----------------------------------------------------------------- upload
def save_upload(filename: str, data: bytes) -> Upload:
    if not filename.lower().endswith(".xlsx"):
        raise ValueError("Hanya file .xlsx yang didukung.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("Ukuran file melebihi 100 MB.")

    upload_id = uuid.uuid4().hex
    folder = Path(tempfile.mkdtemp(prefix="pdrb_"))
    path = folder / "sumber.xlsx"
    path.write_bytes(data)

    try:
        with pd.ExcelFile(path) as xls:
            sheets = list(xls.sheet_names)
        missing = engine.missing_sheets(sheets)
        periods: list[str] = []
        if not missing:
            mapping = engine.build_sheet_mapping(sheets)
            periods = engine.detect_periods(path, mapping["209"])
    except Exception as exc:
        shutil.rmtree(folder, ignore_errors=True)
        raise ValueError(f"File Excel tidak dapat dibaca: {exc}") from exc

    up = Upload(upload_id, filename, path, sheets, missing, periods)
    with _LOCK:
        UPLOADS[upload_id] = up
    return up


# -------------------------------------------------------------------- job
def _run_job(job: Job, upload: Upload) -> None:
    job.status = "running"

    def on_progress(i: int, n: int) -> None:
        job.current, job.total = i, n

    try:
        result = engine.run_evaluation(
            NOTEBOOK_PATH, upload.path, job.periode, upload.sheets, WORK_DIR, on_progress
        )
        df = result.dataframe.rename(columns=API_COLUMNS)
        df["kategori"] = df["evaluasi"].map(kategori_evaluasi)
        job.df = df
        job.output_path = result.output_path
        job.status = "done"
    except Exception as exc:  # noqa: BLE001 - ditampilkan ke pengguna
        job.error = str(exc)
        job.status = "error"


def start_job(upload_id: str, periode: str) -> Job:
    upload = UPLOADS.get(upload_id)
    if upload is None:
        raise KeyError("Upload tidak ditemukan. Unggah ulang file.")
    if upload.missing:
        raise ValueError("Sheet wajib belum lengkap: " + ", ".join(upload.missing))
    if upload.periods and periode not in upload.periods:
        raise ValueError(f"Periode {periode} tidak ada di file. Pilihan: {', '.join(upload.periods)}")
    if not re.match(r"^\d{4}Q[1-4]$", periode):
        raise ValueError("Format periode harus seperti 2026Q3.")

    job = Job(uuid.uuid4().hex, upload_id, periode, upload.filename)
    with _LOCK:
        JOBS[job.id] = job
    _EXECUTOR.submit(_run_job, job, upload)
    return job


def job_status(job: Job) -> dict:
    return {
        "id": job.id,
        "status": job.status,
        "periode": job.periode,
        "source": job.source,
        "current": job.current,
        "total": job.total,
        "error": job.error,
        "created": job.created,
        "total_rows": None if job.df is None else int(len(job.df)),
    }


# ------------------------------------------------------------------ hasil
def _records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records"))  # NaN -> null


def summary(job: Job) -> dict:
    df = job.df
    if df is None:
        return {}

    def top(col: str, n: int) -> list[dict]:
        vc = df[col].value_counts().head(n)
        return [{"label": str(k), "count": int(v)} for k, v in vc.items()]

    return {
        "total": int(len(df)),
        "kabkot_unik": int(df["kabkot"].nunique()),
        "jenis_evaluasi": int(df["kategori"].nunique()),
        "per_kategori": top("kategori", 20),
        "per_komponen": top("komponen", 15),
        "per_kabkot": top("kabkot", 15),
        "per_kabkot_all": top("kabkot", 1000),
        "opsi": {
            "kabkot": sorted(df["kabkot"].unique().tolist()),
            "komponen": sorted(df["komponen"].unique().tolist()),
            "kategori": sorted(df["kategori"].unique().tolist()),
        },
    }


def query_results(
    job: Job,
    kabkot: list[str] | None = None,
    komponen: list[str] | None = None,
    kategori: list[str] | None = None,
    q: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    df = job.df
    if df is None:
        raise ValueError("Hasil belum tersedia.")
    view = df
    if kabkot:
        view = view[view["kabkot"].isin(kabkot)]
    if komponen:
        view = view[view["komponen"].isin(komponen)]
    if kategori:
        view = view[view["kategori"].isin(kategori)]
    if q:
        needle = q.lower()
        mask = (
            view["evaluasi"].str.lower().str.contains(needle, regex=False)
            | view["indikator"].str.lower().str.contains(needle, regex=False)
        )
        view = view[mask]

    page_size = max(1, min(page_size, 500))
    total = int(len(view))
    pages = max(1, -(-total // page_size))
    page = max(1, min(page, pages))
    chunk = view.iloc[(page - 1) * page_size : page * page_size].drop(columns=["kategori"])
    return {"total": total, "page": page, "pages": pages, "page_size": page_size, "rows": _records(chunk)}
