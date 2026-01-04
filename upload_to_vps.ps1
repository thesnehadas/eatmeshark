# PowerShell script to upload files to Hostinger VPS
# Usage: .\upload_to_vps.ps1

$VPS_IP = "62.72.57.117"
$VPS_USER = "root"
$REMOTE_DIR = "/var/www/shark-tank"
$LOCAL_DIR = Get-Location

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Uploading Shark Tank Intelligence Platform" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if SCP is available (requires OpenSSH client on Windows)
$scpPath = Get-Command scp -ErrorAction SilentlyContinue
if (-not $scpPath) {
    Write-Host "Error: SCP not found. Please install OpenSSH client:" -ForegroundColor Red
    Write-Host "  Settings > Apps > Optional Features > OpenSSH Client" -ForegroundColor Yellow
    exit 1
}

Write-Host "Uploading files to $VPS_USER@$VPS_IP:$REMOTE_DIR" -ForegroundColor Yellow
Write-Host ""

# Files and directories to upload (excluding unnecessary files)
$excludePatterns = @(
    "__pycache__",
    "*.pyc",
    ".git",
    "*.log",
    "venv",
    ".env",
    "test_*.py",
    "debug_*.py",
    "*.md"
)

# Create exclude string for scp
$excludeArgs = $excludePatterns | ForEach-Object { "-x $_" }

# Upload files
Write-Host "Uploading application files..." -ForegroundColor Green

# Upload main files
scp -r api.py run_web.py gunicorn_config.py requirements.txt $VPS_USER@$VPS_IP:$REMOTE_DIR/

# Upload directories
Write-Host "Uploading src directory..." -ForegroundColor Green
scp -r src/ $VPS_USER@$VPS_IP:$REMOTE_DIR/

Write-Host "Uploading templates directory..." -ForegroundColor Green
scp -r templates/ $VPS_USER@$VPS_IP:$REMOTE_DIR/

Write-Host "Uploading static directory..." -ForegroundColor Green
scp -r static/ $VPS_USER@$VPS_IP:$REMOTE_DIR/

Write-Host "Uploading models directory..." -ForegroundColor Green
scp -r models/ $VPS_USER@$VPS_IP:$REMOTE_DIR/

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Upload Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps on the VPS:" -ForegroundColor Yellow
Write-Host "  1. SSH into the VPS: ssh $VPS_USER@$VPS_IP" -ForegroundColor White
Write-Host "  2. Run the deployment script: bash deploy.sh" -ForegroundColor White
Write-Host "  3. Or follow manual steps in DEPLOYMENT.md" -ForegroundColor White
Write-Host ""

