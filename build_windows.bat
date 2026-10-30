@echo off
setlocal
cd /d "%~dp0"

echo [1/4] Build frontend
pushd frontend
call npm install || goto :err
call npm run build || goto :err
popd

echo [2/4] Install dependency Python
python -m pip install -r requirements-desktop.txt || goto :err

echo [3/4] Bungkus jadi .exe (PyInstaller)
python -m PyInstaller --noconfirm --clean desktop.spec || goto :err

echo [4/4] Salin main.ipynb ke samping .exe (agar threshold bisa diubah)
copy /Y main.ipynb dist\EvaluasiPDRB\main.ipynb >nul

echo.
echo Selesai: dist\EvaluasiPDRB\EvaluasiPDRB.exe
exit /b 0

:err
echo.
echo GAGAL. Lihat pesan error di atas.
exit /b 1
