; Inno Setup: membuat EvaluasiPDRB-Setup.exe dari hasil PyInstaller (dist\EvaluasiPDRB)
[Setup]
AppName=Evaluasi PDRB Provinsi
AppVersion=1.0.0
DefaultDirName={autopf}\Evaluasi PDRB
DefaultGroupName=Evaluasi PDRB
OutputDir=Output
OutputBaseFilename=EvaluasiPDRB-Setup
SetupIconFile=assets\app.ico
UninstallDisplayIcon={app}\EvaluasiPDRB.exe
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest

[Tasks]
Name: "desktopicon"; Description: "Buat pintasan di desktop"

[Files]
Source: "dist\EvaluasiPDRB\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\Evaluasi PDRB"; Filename: "{app}\EvaluasiPDRB.exe"
Name: "{autodesktop}\Evaluasi PDRB"; Filename: "{app}\EvaluasiPDRB.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\EvaluasiPDRB.exe"; Description: "Jalankan Evaluasi PDRB"; Flags: nowait postinstall skipifsilent
