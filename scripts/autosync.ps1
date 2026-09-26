param([string]$Root='C:\Users\PC1\DreamLab',[int]$PollSeconds=5,[int]$QuietSeconds=8)
$ErrorActionPreference='Continue'
$mutex=New-Object Threading.Mutex($false,'DreamSyncAutoSync-'+$env:USERNAME)
if(-not $mutex.WaitOne(0,$false)){ exit }
$log=Join-Path $Root '.dreamsync-autosync.log'
$cli='C:\Users\PC1\DreamLab\DreamSync\dreamsync.cmd'
$seen=@{}
function Log([string]$m){ Add-Content $log "$(Get-Date -Format s) $m" }
Log 'AUTOSYNC_VERIFIED_START'
while($true){
  Get-ChildItem $Root -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $repo=$_.FullName; $name=$_.Name
    if(!(Test-Path (Join-Path $repo '.git')) -or !(Test-Path (Join-Path $repo '.dreamsync\project.yml'))){ return }
    $dirty=[bool](@(& git -C $repo status --porcelain=v1 --untracked-files=all 2>$null))
    if(!$dirty){
      $seen.Remove($name) | Out-Null
      & git -C $repo fetch -q origin main 2>$null
      $head=(& git -C $repo rev-parse HEAD 2>$null).Trim()
      $remote=(& git -C $repo rev-parse origin/main 2>$null).Trim()
      if($head -and $remote -and $head -ne $remote){
        & git -C $repo merge --ff-only origin/main 2>$null
        if($LASTEXITCODE -eq 0){ Log "PULLED $name $remote" }
      }
      return
    }
    $now=[DateTime]::UtcNow
    if(!$seen.ContainsKey($name)){ $seen[$name]=$now; return }
    if(($now-$seen[$name]).TotalSeconds -lt $QuietSeconds){ return }
    $seen[$name]=$now.AddYears(1)
    Log "VERIFYING $name"
    $msg='autosync: '+(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    & $cli finish --root $repo --message $msg >> $log 2>&1
    if($LASTEXITCODE -eq 0){ Log "VERIFIED_SYNCED $name" } else { Log "BLOCKED $name"; $seen[$name]=$now }
  }
  Start-Sleep -Seconds $PollSeconds
}
