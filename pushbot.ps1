Write-Host "`n🚀 PUSHBOT LOCAL SYNC" -ForegroundColor Cyan
Set-Location $PSScriptRoot

git status
git add .
git commit -m "🧠 Local PushBot sync from Cursor" | Out-Null
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Push completed — GitHub synced!" -ForegroundColor Green
    Write-Host "🌐 Next step: SSH into server and run 'updatebot DreamSync'" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Push failed — check credentials or network." -ForegroundColor Red
}