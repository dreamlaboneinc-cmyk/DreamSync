param([string]$Root='C:\\Users\\PC1\\DreamLab',[int]$PollSeconds=5)
$ErrorActionPreference='Continue'
$mutex=New-Object Threading.Mutex($false,'DreamSyncAutoSync-'+$env:USERNAME)
if(-not $mutex.WaitOne(0,$false)){ exit }
$log=Join-Path $Root '.dreamsync-autosync.log'
$registry=Join-Path $Root 'DreamSync\fleet\projects.txt'
function Log([string]$m){ Add-Content $log "$(Get-Date -Format s) $m" }
New-Item -ItemType Directory -Force -Path (Split-Path $registry) | Out-Null
Log 'AUTOSYNC_START'
while($true){
  $repos=@(Get-ChildItem $Root -Directory -ErrorAction SilentlyContinue | Where-Object { Test-Path (Join-Path $_.FullName '.git') })
  $names=@($repos | Select-Object -ExpandProperty Name | Sort-Object)
  $wanted=($names -join [Environment]::NewLine)+[Environment]::NewLine
  $current=if(Test-Path $registry){ Get-Content -Raw $registry }else{ '' }
  if($current -ne $wanted){ Set-Content -Path $registry -Value $wanted -NoNewline; Log 'REGISTRY_UPDATED' }
  foreach($item in $repos){
    $repo=$item.FullName; $name=$item.Name; $newOrigin=$false
    & git -C $repo remote get-url origin 1>$null 2>$null
    if($LASTEXITCODE -ne 0){
      & gh repo view "dreamlaboneinc-cmyk/$name" 1>$null 2>$null
      if($LASTEXITCODE -ne 0){ & gh repo create "dreamlaboneinc-cmyk/$name" --private --disable-issues --disable-wiki 1>$null 2>$null }
      & git -C $repo remote add origin "https://github.com/dreamlaboneinc-cmyk/$name.git" 2>$null
      $newOrigin=$true; Log "ORIGIN_READY $name"
    }
    $dirty=@(& git -C $repo status --porcelain=v1 --untracked-files=all 2>$null)
    if(!$dirty){
      if($newOrigin){ & git -C $repo push -q -u origin main 2>$null; if($LASTEXITCODE -eq 0){ Log "PUSHED_INITIAL $name" } }
      continue
    }
    & git -C $repo diff --check 2>$null
    if($LASTEXITCODE -ne 0){ Log "BLOCKED_DIFFCHECK $name"; continue }
    & git -C $repo add -A 2>$null
    $staged=@(& git -C $repo diff --cached --name-only 2>$null)
    if(!$staged){ continue }
    $bad=@($staged | Where-Object { $_ -match '(^|/)(\.env($|\.)|.*\.(key|pem|db|sqlite|sqlite3|log|pid)$)' })
    if($bad){ & git -C $repo reset -q 2>$null; Log "BLOCKED_PROTECTED $name"; continue }
    $msg='autosync: '+(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
    & git -C $repo commit -q -m $msg 2>$null
    if($LASTEXITCODE -ne 0){ continue }
    & git -C $repo push -q -u origin main 2>$null
    if($LASTEXITCODE -eq 0){ $sha=& git -C $repo rev-parse HEAD 2>$null; Log "PUSHED $name $sha" } else { Log "PUSH_FAILED $name" }
  }
  Start-Sleep -Seconds $PollSeconds
}
