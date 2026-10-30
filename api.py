"""FastAPI untuk Sistem Evaluasi PDRB Provinsi.

Jalankan:  uvicorn api:app --reload      (dokumentasi API: http://127.0.0.1:8000/docs)
"""
from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import service
from paths import DIST_DIR


app = FastAPI(title="Evaluasi PDRB Provinsi", version="1.0.0")


class RunRequest(BaseModel):
    upload_id: str
    periode: str


def _job_or_404(job_id: str) -> service.Job:
    job = service.JOBS.get(job_id)
    if job is None:
        raise HTTPException(404, "Job tidak ditemukan.")
    return job


def _done_job_or_409(job_id: str) -> service.Job:
    job = _job_or_404(job_id)
    if job.status != "done":
        raise HTTPException(409, f"Job belum selesai (status: {job.status}).")
    return job


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "notebook": service.NOTEBOOK_PATH.exists()}


@app.post("/api/inspect")
def inspect_file(file: UploadFile = File(...)) -> dict:
    """Unggah Excel sumber; kembalikan upload_id, sheet, sheet yang kurang, dan periode."""
    try:
        up = service.save_upload(file.filename or "", file.file.read())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "upload_id": up.id,
        "filename": up.filename,
        "sheets": up.sheets,
        "missing": up.missing,
        "periods": up.periods,
    }


@app.post("/api/run", status_code=202)
def run(req: RunRequest) -> dict:
    """Jalankan evaluasi di latar belakang; pantau lewat GET /api/jobs/{id}."""
    if not service.NOTEBOOK_PATH.exists():
        raise HTTPException(500, "main.ipynb tidak ditemukan di folder aplikasi.")
    try:
        job = service.start_job(req.upload_id, req.periode)
    except KeyError as exc:
        raise HTTPException(404, str(exc.args[0])) from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return service.job_status(job)


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    return service.job_status(_job_or_404(job_id))


@app.get("/api/jobs/{job_id}/summary")
def get_summary(job_id: str) -> dict:
    return service.summary(_done_job_or_409(job_id))


@app.get("/api/jobs/{job_id}/results")
def get_results(
    job_id: str,
    kabkot: list[str] | None = Query(None),
    komponen: list[str] | None = Query(None),
    kategori: list[str] | None = Query(None),
    q: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    job = _done_job_or_409(job_id)
    return service.query_results(job, kabkot, komponen, kategori, q, page, page_size)


@app.get("/api/jobs/{job_id}/download")
def download(job_id: str) -> FileResponse:
    job = _done_job_or_409(job_id)
    assert job.output_path is not None
    return FileResponse(
        job.output_path,
        filename=job.output_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# Frontend Vue (hasil `npm run build`). Dipasang terakhir agar tidak menimpa /api dan /docs.
if DIST_DIR.exists():
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="frontend")
else:

    @app.get("/")
    def root() -> dict:
        return {
            "message": "Frontend belum di-build. Jalankan `npm run build` di folder frontend/, "
            "atau pakai `npm run dev` (http://localhost:5173) saat pengembangan.",
            "docs": "/docs",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=False)
