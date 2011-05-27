[Setup]
AppName=Market
AppVerName=Market v1.40
DefaultDirName={pf}\Market
DefaultGroupName=Market
UninstallDisplayIcon={app}\Market.exe
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=none

[Dirs]
Name: "{app}\"; Permissions: everyone-modify

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"

[Files]
Source: "dist/market.exe"; DestDir: "{app}"; Permissions: users-modify
Source: "dist/mpl-data/*"; DestDir: "{app}/mpl-data"; Permissions: users-modify
Source: "dist/python25.dll"; DestDir: "{app}"; Permissions: users-modify
Source: "dist/w9xpopen.exe"; DestDir: "{app}"; Permissions: users-modify
Source: "dist/*"; DestDir: "{app}"; Permissions: users-modify
Source: "dist/market.ico"; DestDir: "{app}"; Permissions: users-modify

[Icons]
Name: "{group}\Market"; Filename: "{app}\market.exe"; WorkingDir: "{app}"
Name: "{group}\Uninstall Market App"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Market"; Filename: "{app}\market.exe"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\market.exe"; Description: "Launch Market App"; Flags: nowait postinstall skipifsilent
