param([string]$Root='C:\\Users\\PC1\\DreamLab',[int]$PollSeconds=5)
$ErrorActionPreference='Continue'
$mutex=New-Object Threading.Mutex($false,'DreamSyncAutoSync-'+$env:USERNAME)
if(-not $mutex.WaitOne(0,$false)){ exit }
$log=Join-Path $Root '.dreamsync-autosync.log'
function Log([string]$m){ Add-Content $log "$(Get-Date -Format s) $m" }
Log 'AUTOSYNC_START'
while($true){
  Get-ChildItem $Root -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $repo=$_.FullName; $name=$_.Name
    if(!(Test-Path (Join-Path $repo '.git'))){ return }
    $dirty=@(& git -C $repo status --porcelain=v1 --untracked-files=all 2>$null)
    if(!$dirty){
      & git -C $repo fetch -q origin main 2>$null
      $head=& git -C $repo rev-parse HEAD 2>$null
      $remote=& git -C $repo rev-parse origin/main 2>$null
      if($head -and $remote -and $head -ne $remote){
        & git -C $repo merge --ff-only origin/main 2>$null
        if($LASTEXITCODE -eq 0){ Log "PULLED $name $remote" }
      }
      return
    }
    & git -C $repo diff --check 2>$null
    if($LASTEXITCODE -ne 0){ Log "BLOCKED_DIFFCHECK $name"; return }
    & git -C $repo add -A 2>$null
    $staged=@(& git -C $repo diff --cached --name-only 2>$null)
    if(!$staged){ return }
    $bad=@($staged | Where-Object { $_ -match '(^|/)(\.env($|\.)|.*\.(key|pem|db|sqlite|sqlite3|log|pid)$)' })
    if($bad){ & git -C $repo reset -q 2>$null; Log "BLOCKED_PROTECTED $name"; return }
    $msg='autosync: '+(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    & git -C $repo commit -q -m $msg 2>$null
    if($LASTEXITCODE -ne 0){ return }
    & git -C $repo push -q origin main 2>$null
    if($LASTEXITCODE -ne 0){ Log "PUSH_FAILED $name"; return }
    $sha=& git -C $repo rev-parse HEAD 2>$null
    $remoteCmd="cd /root/apps/$name && git fetch -q origin main && git reset -q --hard origin/main"
    & ssh sacredlight $remoteCmd 2>$null
    if($LASTEXITCODE -eq 0){ Log "SYNCED $name $sha" } else { Log "SERVER_SYNC_FAILED $name $sha" }
  }
  Start-Sleep -Seconds $PollSeconds
}
