[Setup]
AppName=OmniBoard Studio
AppVersion=0.12
DefaultDirName={localappdata}\OmniBoard Studio
DefaultGroupName=OmniBoard Studio
PrivilegesRequired=lowest
OutputDir=.
OutputBaseFilename=OmniBoard_Online_Installer
SolidCompression=yes

[Code]
var DownloadPage: TDownloadWizardPage;

procedure InitializeWizard;
begin
  DownloadPage := CreateDownloadPage('Downloading OmniBoard Studio', 'Please wait...', nil);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var ResultCode: Integer;
begin
  Result := True;
  if CurPageID = wpReady then begin
    DownloadPage.Clear;
    // Updated to latest release URL
    DownloadPage.Add('https://github.com/Kotoad/APP_PyQt/releases/latest/download/OmniBoard_Studio_Windows.zip', 'OmniBoard.zip', '');
    DownloadPage.Show;
    try
      try
        DownloadPage.Download;
        ForceDirectories(ExpandConstant('{app}'));
        // Use Windows native tar to unzip the .zip file
        Exec('tar.exe', '-xf "' + ExpandConstant('{tmp}\OmniBoard.zip') + '" -C "' + ExpandConstant('{app}') + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      except
        MsgBox('Installation failed.', mbError, MB_OK);
        Result := False;
      end;
    finally
      DownloadPage.Hide;
    end;
  end;
end;