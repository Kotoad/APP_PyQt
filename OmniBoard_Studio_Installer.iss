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

function NextButtonClick(CurPageID: Integer): Boolean;
var ResultCode: Integer;
begin
  Result := True;
  
  if CurPageID = wpReady then begin
    // 1. Force kill the running application to unlock files
    Exec('taskkill.exe', '/F /IM "OmniBoard Studio.exe"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Sleep(1500); // 2. Wait 1.5 seconds for Windows to clear the file handles

    DownloadPage.Clear;
    DownloadPage.Add('https://github.com/Kotoad/APP_PyQt/releases/latest/download/OmniBoard_Studio_Windows.zip', 'OmniBoard.zip', '');
    DownloadPage.Show;
    
    try
      try
        DownloadPage.Download;
        ForceDirectories(ExpandConstant('{app}'));
        
        // 3. Extract the files
        Exec('tar.exe', '-xf "' + ExpandConstant('{tmp}\OmniBoard.zip') + '" -C "' + ExpandConstant('{app}') + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
        
        // 4. Check for silent extraction failures
        if ResultCode <> 0 then begin
          if not WizardSilent() then begin
            MsgBox('Extraction failed. Windows may still be locking the files. Result Code: ' + IntToStr(ResultCode), mbError, MB_OK);
          end;
          Result := False;
        end else begin
          InstallSuccessful := True;
        end;
        
      except
        if not WizardSilent() then begin
          MsgBox('Installation failed.', mbError, MB_OK);
        end;
        Result := False;
      end;
    finally
      DownloadPage.Hide;
    end;
  end;
end;