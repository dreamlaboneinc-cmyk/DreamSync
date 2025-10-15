Write-Host "`n🧠 Activating DreamSync Virtual Environment..." -ForegroundColor Cyan
Set-Location $PSScriptRoot

$venvPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    & $venvPath
    Write-Host "✅ venv activated successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ venv not found! Run: python -m venv venv" -ForegroundColor Red
}