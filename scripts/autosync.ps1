param([string]$Root='C:\\Users\\PC1\\DreamLab',[int]$PollSeconds=3,[int]$StableSeconds=10)
$ErrorActionPreference='Continue'
$mutex=New-Object Threading.Mutex($false,'DreamSyncAutoSync-'+$env:USERNAME)
if(-not $mutex.WaitOne(0,$false)){ exit }
$state=@{}
$log=Join-Path $Root '.dreamsync-autosync.log'
function Log([string]$m){ Add-Content $log "$(Get-Date -Format s) $m" }
function Finger([string]$repo){
  $s=(& git -C $repo status --porcelain=v1 --untracked-files=all 2>$null) -join [Environment]::NewLine
  if([string]::IsNullOrWhiteSpace($s)){ return '' }
  $d=(& git -C $repo diff --no-ext-diff 2>$null) -join [Environment]::NewLine
  $bytes=[Text.Encoding]::UTF8.GetBytes($s+$d)
  $sha=[Security.Cryptography.SHA256]::Create()
  return [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-','')
}
Log 'AUTOSYNC_START'
while($true){
  Get-ChildItem $Root -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $repo=$_.FullName; $name=$_.Name
    if(!(Test-Path (Join-Path $repo '.git'))){ return }
    $fp=Finger $repo
    if(!$fp){
      $state.Remove($repo)
      & git -C $repo fetch -q origin main 2>$null
      $head=& git -C $repo rev-parse HEAD 2>$null
      $remote=& git -C $repo rev-parse origin/main 2>$null
      if($head -and $remote -and $head -ne $remote){
        & git -C $repo merge --ff-only origin/main 2>$null
        if($LASTEXITCODE -eq 0){ Log "PULLED $name $remote" }
      }
      return
    }
    $now=Get-Date
    if(!$state.ContainsKey($repo) -or $state[$repo].fp -ne $fp){ $state[$repo]=@{fp=$fp;since=$now}; return }
    if(($now-$state[$repo].since).TotalSeconds -lt $StableSeconds){ return }
    & git -C $repo diff --check 2>$null
    if($LASTEXITCODE -ne 0){ Log "BLOCKED_DIFFCHECK $name"; $state[$repo].since=$now; return }
    & git -C $repo add -A 2>$null
    $staged=@(& git -C $repo diff --cached --name-only 2>$null)
    if(!$staged){ $state.Remove($repo); return }
    $bad=@($staged | Where-Object { $_ -match '(^|/)(\.env($|\.)|.*\.(key|pem|db|sqlite|sqlite3|log|pid)$)' })
    if($bad){ & git -C $repo reset -q 2>$null; Log "BLOCKED_PROTECTED $name"; $state[$repo].since=$now; return }
    $msg='autosync: '+(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    & git -C $repo commit -q -m $msg 2>$null
    if($LASTEXITCODE -eq 0){
      & git -C $repo push -q origin main 2>$null
      if($LASTEXITCODE -eq 0){
        $sha=& git -C $repo rev-parse HEAD 2>$null
        $remoteCmd="cd /root/apps/$name && git fetch -q origin main && git reset -q --hard origin/main"
        & ssh sacredlight $remoteCmd 2>$null
        if($LASTEXITCODE -eq 0){ Log "SYNCED $name $sha" } else { Log "SERVER_SYNC_FAILED $name $sha" }
      } else { Log "PUSH_FAILED $name" }
    }
    $state.Remove($repo)
  }
  Start-Sleep -Seconds $PollSeconds
}
