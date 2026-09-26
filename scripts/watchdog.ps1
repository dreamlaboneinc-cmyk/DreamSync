$ErrorActionPreference = 'SilentlyContinue'
$autosync = 'C:\Users\PC1\DreamLab\DreamSync\scripts\autosync.ps1'
while ($true) {
  $running = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like '*DreamSync*autosync.ps1*' -and
    $_.ProcessId -ne $PID -and
    $_.CommandLine -notlike '*watchdog.ps1*'
  }
  if (-not $running) {
    Start-Process powershell.exe -WindowStyle Hidden -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',$autosync)
  }
  Start-Sleep -Seconds 20
}
