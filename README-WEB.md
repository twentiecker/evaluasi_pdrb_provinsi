# Sistem Evaluasi PDRB Provinsi (FastAPI + Vue 3)

Logika evaluasi tetap dijalankan oleh `main.ipynb` (sel kode dieksekusi apa adanya oleh `engine.py`).
`main.ipynb` tidak diubah.

```text
evaluasi_pdrb_gui/
├── main.ipynb
├── engine.py            # menjalankan sel notebook + patch konfigurasi
├── service.py           # upload, antrian job, filter dan ringkasan
├── api.py               # endpoint FastAPI (+ menyajikan frontend/dist)
├── requirements-api.txt
├── Export Semua Tabel Resume_olah (contoh).xlsx   # data contoh untuk uji
└── frontend/            # Vue 3 + Vite
```

## Backend
```bash
python -m venv venv && venv\Scripts\activate     # Mac/Linux: source venv/bin/activate
pip install -r requirements-api.txt
uvicorn api:app --reload                         # http://127.0.0.1:8000  (dokumentasi API: /docs)
```

## Frontend, mode pengembangan (Node.js 18+)
```bash
cd frontend
npm install
npm run dev                                      # http://localhost:5173 (/api diproksikan ke :8000)
```

## Frontend, mode produksi (satu server)
```bash
cd frontend && npm install && npm run build
cd .. && uvicorn api:app                         # http://127.0.0.1:8000
```

Font (Bricolage Grotesque dan Instrument Sans) dipasang lewat npm dan ikut ter-bundle,
jadi aplikasi tetap tampil benar tanpa koneksi internet setelah `npm install`.
