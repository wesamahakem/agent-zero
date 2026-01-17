# PowerShell script to sync with upstream/development
# Usage: ./sync-upstream.ps1

Write-Host "Syncing with upstream/development..." -ForegroundColor Cyan

# Fetch from upstream
git fetch upstream

# Try to merge
$mergeOutput = git merge upstream/development --no-edit 2>&1
$mergeExitCode = $LASTEXITCODE

if ($mergeExitCode -eq 0) {
    Write-Host "✓ Successfully synced with upstream/development" -ForegroundColor Green
    exit 0
} else {
    Write-Host "⚠ Auto-sync failed - merge conflicts detected" -ForegroundColor Yellow
    Write-Host "Please resolve conflicts manually and run:" -ForegroundColor Yellow
    Write-Host "  git merge --abort   (to cancel)" -ForegroundColor Yellow
    Write-Host "  git merge --continue (to complete after resolving)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host $mergeOutput
    exit 1
}
