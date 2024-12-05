[Setup]
AppName=Christ0$
AppVersion=1.0
DefaultDirName={userappdata}\Christ0$
DefaultGroupName=Christ0$
OutputDir=C:\Users\ASUS\Desktop\Planner programm\Planner
OutputBaseFilename=Christ0$_Setup_V1
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
Source: "dist\assets\*"; DestDir: "{app}\assets"; Flags: recursesubdirs
Source: "dist\data\*"; DestDir: "{app}\data"; Flags: recursesubdirs
Source: "dist\src\*"; DestDir: "{app}\src"; Flags: recursesubdirs
Source: "dist\config\*"; DestDir: "{app}\config"; Flags: recursesubdirs
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Christ0$"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"
Name: "{userdesktop}\Christ0$"; Filename: "{app}\main.exe"; IconFilename: "{app}\icon.ico"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\Christ0$"; ValueType: string; ValueName: "DisplayName"; ValueData: "Christ0$"
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\Christ0$"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{app}\main.exe"

[Code]
procedure SetWritePermissions;
begin
  // Устанавливаем разрешения на запись в папке с данными (например, AppData)
  SetAccessRights('{app}\data', 'Users', 'fullaccess');
  SetAccessRights('{app}\config', 'Users', 'fullaccess');
end;