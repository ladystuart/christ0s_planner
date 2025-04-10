[Setup]
AppName=Christ0$
AppId={{6E8D7461-11C8-409C-BAC6-21121836B2AF}}
AppVersion=2.0
DefaultDirName={sd}\Christ0$
DefaultGroupName=Christ0$
OutputDir=C:\Users\ASUS\Desktop\Planner program\Planner frontend PUBLIC
OutputBaseFilename=Christ0$_Setup_V2
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
WizardStyle=modern
DisableDirPage=no
DisableProgramGroupPage=no
AllowNoIcons=no
SetupIconFile=icon.ico
PrivilegesRequired=admin

[Files]
Source: "dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\data\*"; DestDir: "{app}\data"; Flags: recursesubdirs
Source: "dist\src\*"; DestDir: "{app}\src"; Flags: recursesubdirs
Source: "dist\config\*"; DestDir: "{app}\config"; Flags: recursesubdirs
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Christ0$"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"
Name: "{userdesktop}\Christ0$"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\Christ0$"; ValueType: string; ValueName: "DisplayName"; ValueData: "Christ0$"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\Christ0$"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\icon.ico"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\Christ0$"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{#SetupSetting("AppVersion")}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\Christ0$"; ValueType: string; ValueName: "Publisher"; ValueData: "Lady Stuart"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\Christ0$"; ValueType: string; ValueName: "UninstallString"; ValueData: "{uninstallexe}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\Christ0$"; ValueType: string; ValueName: "QuietUninstallString"; ValueData: "{uninstallexe} /SILENT"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\Christ0$"; ValueType: dword; ValueName: "NoModify"; ValueData: 1
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\Christ0$"; ValueType: dword; ValueName: "NoRepair"; ValueData: 1

[Code]
procedure SetWritePermissions;
var
  ResultCode: Integer;
begin
  // Grant full access to "Users" group for data, src and config folders
  Exec('icacls', ExpandConstant('"{app}\data"') + ' /grant Users:(OI)(CI)F /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('icacls', ExpandConstant('"{app}\config"') + ' /grant Users:(OI)(CI)F /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  Exec('icacls', ExpandConstant('"{app}\src"') + ' /grant Users:(OI)(CI)F /T', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;