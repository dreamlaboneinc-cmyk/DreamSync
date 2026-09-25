$ErrorActionPreference = "Stop"
Write-Host "DreamSync V2 verification gate..."
python -m dreamsync.cli verify
if ($LASTEXITCODE -ne 0) { throw "Verification failed. Commit/push blocked." }
Write-Host "VERIFIED. Use DreamSync promotion to commit/push the verified snapshot."
