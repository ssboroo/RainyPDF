#define AppVersion "0.1.0"
[Setup]
AppId={{9A11CB76-1EC4-41E0-87D4-521E5E113040}
AppName=RAINY PDF
AppVersion={#AppVersion}
AppPublisher=RAINY
DefaultDirName={localappdata}\Programs\RainyPDF
DefaultGroupName=RAINY PDF
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=release
OutputBaseFilename=RainyPDF-{#AppVersion}-Setup
SetupIconFile=src\rainypdf\assets\rainypdf.ico
UninstallDisplayIcon={app}\RainyPDF.exe
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
LicenseFile=LICENSE
[Files]
Source: "dist\RainyPDF\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Tasks]
Name: "desktopicon"; Description: "Desktop дээр RAINY PDF дүрс үүсгэх"; Flags: checkedonce
[Icons]
Name: "{group}\RAINY PDF"; Filename: "{app}\RainyPDF.exe"
Name: "{autodesktop}\RAINY PDF"; Filename: "{app}\RainyPDF.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\RainyPDF.exe"; Description: "RAINY PDF нээх"; Flags: nowait postinstall skipifsilent
