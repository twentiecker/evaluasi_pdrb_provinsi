# Aplikasi desktop (Windows .exe)

Aplikasi desktop = backend FastAPI + tampilan Vue yang dibungkus jendela native
(pywebview, memakai Microsoft Edge WebView2) lalu dikemas PyInstaller menjadi `.exe`.
Pengguna tidak perlu memasang Python atau Node.js.

> Build harus dilakukan di Windows (PyInstaller tidak bisa membuat .exe dari Linux/macOS).

## Cara A: build otomatis lewat GitHub (disarankan, tanpa menyiapkan apa pun di PC)
1. Unggah folder proyek ini ke repository GitHub (isi folder ini ada di root repo).
2. Tab **Actions** → **Build aplikasi Windows** → **Run workflow**.
3. Setelah selesai (sekitar 5–10 menit), unduh artifact **EvaluasiPDRB-windows**:
   - `EvaluasiPDRB-windows.zip` → versi portabel (ekstrak, jalankan `EvaluasiPDRB.exe`)
   - `EvaluasiPDRB-Setup.exe` → installer (jika langkah installer berhasil)
4. Untuk rilis yang bisa diunduh publik: `git tag v1.0.0 && git push --tags`.
   File yang sama otomatis terlampir di halaman **Releases**.

## Cara B: build di PC Windows sendiri
Butuh Python 3.10+ dan Node.js 18+.
```bat
build_windows.bat
```
Hasil: `dist\EvaluasiPDRB\EvaluasiPDRB.exe`. Untuk installer, pasang Inno Setup lalu
jalankan `ISCC.exe installer.iss` (hasil: `Output\EvaluasiPDRB-Setup.exe`).

## Uji tanpa membuat .exe
```bash
cd frontend && npm install && npm run build && cd ..
pip install -r requirements-desktop.txt
python desktop.py
```

## Perilaku aplikasi
- `main.ipynb` ada di samping `EvaluasiPDRB.exe`. Edit file itu untuk mengubah threshold; aplikasi memakai versi terbaru saat evaluasi dijalankan.
- Hasil evaluasi disimpan di `data\output\` di samping `.exe` (atau `Documents\Evaluasi PDRB\data\output` bila folder tidak bisa ditulis). Tombol **Unduh Excel** membuka dialog "Simpan sebagai"; **Buka folder hasil** membuka foldernya.
- Log galat: `evaluasi_pdrb.log` di folder kerja.
- Jika WebView2 tidak ada, aplikasi otomatis membuka browser bawaan dan menampilkan jendela kecil untuk menghentikannya.

## Catatan
- Ukuran folder hasil build sekitar 150–300 MB (pandas dan numpy ikut dibundel).
- `.exe` tanpa tanda tangan digital bisa memunculkan peringatan Windows SmartScreen ("Run anyway") dan sesekali terdeteksi keliru oleh antivirus. Itu umum untuk hasil PyInstaller; tanda tangan kode (code signing) menghilangkannya.
- Kalau library baru dipakai di `main.ipynb`, tambahkan namanya ke `hiddenimports` di `desktop.spec`, karena notebook dijalankan lewat `exec()` dan tidak terdeteksi otomatis oleh PyInstaller.
