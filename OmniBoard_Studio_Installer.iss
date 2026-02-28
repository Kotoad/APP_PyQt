[Setup]
AppId={{2A6A9E8F-4B1C-4D3E-8F9A-1B2C3D4E5F6A}
AppName=OmniBoard Studio
AppVersion=Latest
DefaultDirName={localappdata}\OmniBoard Studio
DefaultGroupName=OmniBoard Studio
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=OmniBoard_Online_Installer
SolidCompression=yes
DisableDirPage=no
UninstallDisplayIcon={app}\OmniBoard Studio.exe
SetupIconFile=resources\images\Appicon.ico

[Tasks]
Name: "desctopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Icons]
Name: "{group}\Omniboard Studio"; Filename: "{app}\Omniboard Studio.exe"; WorkingDir: "{app}"
Name: "{group}\Uninstall OmniBoard Studio"; Filename: "{uninstallexe}"
Name: "{autodesktop}\OmniBoard Studio"; Filename: "{app}\Omniboard Studio.exe"; WorkingDir: "{app}"; Tasks: desctopicon

[Run]
Filename: "{app}\Omniboard Studio.exe"; Description: "Launch OmniBoard Studio"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
var DownloadPage: TDownloadWizardPage;
    InstallSuccessful: Boolean;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage('Downloading OmniBoard Studio', 'Please wait...', nil);
end;

procedure DeinitializeSetup();
var
  ErrorCode: Integer;
begin
  if InstallSuccessful then begin
    Exec('cmd.exe', '/c ping 127.0.0.1 -n 3 > nul & del "' + ExpandConstant('{srcexe}') + '"', '', SW_HIDE, ewNoWait, ErrorCode);
  end;
end;

// Move the logic here so it triggers even in /SILENT mode
procedure CurStepChanged(CurStep: TSetupStep);
var ResultCode: Integer;
begin
  if CurStep = ssInstall then begin
    // 1. Force kill the app (using full path to taskkill for reliability)
    Exec(ExpandConstant('{sys}\taskkill.exe'), '/F /IM "OmniBoard Studio.exe"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Sleep(2000); // Give Windows time to release file handles

    DownloadPage.Clear;
    DownloadPage.Add('https://github.com/Kotoad/APP_PyQt/releases/latest/download/OmniBoard_Studio_Windows.zip', 'OmniBoard.zip', '');
    
    // Only show the UI if we aren't in silent mode
    if not WizardSilent then DownloadPage.Show;
    
    try
      DownloadPage.Download;
      ForceDirectories(ExpandConstant('{app}'));
      
      // Extract using tar
      Exec(ExpandConstant('{sys}\tar.exe'), 
           '-xf "' + ExpandConstant('{tmp}\OmniBoard.zip') + '" -C "' + ExpandConstant('{app}') + '"', 
           '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
           
      if ResultCode = 0 then InstallSuccessful := True;
    finally
      if not WizardSilent then DownloadPage.Hide;
    end;
  end;
end;