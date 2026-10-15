$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONPATH = Join-Path $PSScriptRoot '..\src'
function Check([string]$step) { if ($LASTEXITCODE -ne 0) { throw "$step failed ($LASTEXITCODE)" } }
python -m pip install -r requirements-dev.txt
Check 'Dependencies'
python build-tools/fetch_runtimes.py
Check 'Runtimes'
$env:QT_QPA_PLATFORM = 'offscreen'
python -m pytest -q
Check 'Tests'
Remove-Item Env:QT_QPA_PLATFORM
python -m PyInstaller --noconfirm --clean --onedir --windowed --name RainyPDF --paths src --collect-data rainypdf --collect-all pymupdf --icon src/rainypdf/assets/rainypdf.ico build-tools/entry.py
Check 'PyInstaller'
Copy-Item runtimes dist/RainyPDF/runtimes -Recurse -Force
Copy-Item LICENSE,THIRD-PARTY-NOTICES.md,README.md dist/RainyPDF/ -Force
Copy-Item docs/USER-GUIDE-MN.md dist/RainyPDF/ -Force
python build-tools/smoke_windows.py dist/RainyPDF/RainyPDF.exe
Check 'Packaged smoke'
$iscc = Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'
& $iscc installer.iss
Check 'Installer'
$installPath = Join-Path $env:TEMP 'RainyPDF-install-check'
$installer = Join-Path $PWD 'release/RainyPDF-0.1.0-Setup.exe'
$p = Start-Process $installer -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART',('/DIR="' + $installPath + '"')) -PassThru -Wait
if ($p.ExitCode -ne 0) { throw 'Installer test failed' }
python build-tools/smoke_windows.py (Join-Path $installPath 'RainyPDF.exe')
Check 'Installed smoke'
$p = Start-Process (Join-Path $installPath 'unins000.exe') -ArgumentList @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART') -Wait -PassThru
if ($p.ExitCode -ne 0) { throw 'Uninstall failed' }
