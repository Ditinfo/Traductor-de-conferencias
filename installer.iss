; Script de Inno Setup: genera un instalador (TraductorEnVivo-Setup.exe)
; para repartir en varias computadoras sin necesitar Python instalado.
;
; 1) Descargar e instalar Inno Setup (gratis): https://jrsoftware.org/isinfo.php
; 2) Correr primero build_exe.bat para generar dist\TraductorEnVivo.exe
; 3) Abrir este archivo (installer.iss) con Inno Setup y presionar "Compile"
; 4) El instalador final queda en la carpeta Output\

[Setup]
AppName=Traductor en Vivo
AppVersion=1.0
AppPublisher=DIT Informatica
DefaultDirName={autopf}\TraductorEnVivo
DefaultGroupName=Traductor en Vivo
OutputDir=Output
OutputBaseFilename=TraductorEnVivo-Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
DisableProgramGroupPage=yes
PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Files]
Source: "dist\TraductorEnVivo.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Traductor en Vivo"; Filename: "{app}\TraductorEnVivo.exe"
Name: "{autodesktop}\Traductor en Vivo"; Filename: "{app}\TraductorEnVivo.exe"

[Run]
Filename: "{app}\TraductorEnVivo.exe"; Description: "Abrir Traductor en Vivo"; Flags: nowait postinstall skipifsilent
