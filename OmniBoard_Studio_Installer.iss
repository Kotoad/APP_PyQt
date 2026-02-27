[Setup]
AppName=OmniBoard Studio
AppVersion=0.11
DefaultDirName={localappdata}\OmniBoard Studio
DefaultGroupName=OmniBoard Studio
PrivilegesRequired=lowest
OutputDir=dist
OutputBaseFilename=OmniBoard_Online_Installer
SolidCompression=yes

[Icons]
Name: "{group}\OmniBoard Studio"; Filename: "{app}\OmniBoard Studio.exe"
Name: "{userdesktop}\OmniBoard Studio"; Filename: "{app}\OmniBoard Studio.exe"

[Code]
var
  DownloadPage: TDownloadWizardPage;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage('Downloading OmniBoard Studio', 'Please wait while setup downloads the application files...', nil);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  if CurPageID = wpReady then begin
    DownloadPage.Clear;
    DownloadPage.Add('https://github.com/Kotoad/APP_PyQt/releases/download/V0.11/OmniBoard.Studio.zip', 'OmniBoard.zip', '');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download;
        ForceDirectories(ExpandConstant('{app}'));
        { Extract using native Windows tar command }
        Exec('tar.exe', '-xf "' + ExpandConstant('{tmp}\OmniBoard.zip') + '" -C "' + ExpandConstant('{app}') + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      except
        MsgBox('Installation failed. Check your internet connection.', mbError, MB_OK);
        Result := False;
      end;
    finally
      DownloadPage.Hide;
    end;
  end;
end;