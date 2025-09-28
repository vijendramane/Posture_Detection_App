# Posture Detection App Setup Script
Write-Host "Setting up Posture Detection App..." -ForegroundColor Green

# Check if Python is installed or not 
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.9+ first." -ForegroundColor Red
    exit 1
}
 
# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js is not installed or not in PATH. Please install Node.js 16+ first." -ForegroundColor Red
    exit 1
}

# Setup Backend
Write-Host "`nSetting up Backend..." -ForegroundColor Yellow
Set-Location backend

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Go back to root directory
Set-Location ..

# Setup Frontend
Write-Host "`nSetting up Frontend..." -ForegroundColor Yellow
Set-Location frontend

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Cyan
npm install

# Go back to root directory
Set-Location ..

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "`nTo start the application:" -ForegroundColor Yellow
Write-Host "1. Start Backend: cd backend && venv\Scripts\Activate.ps1 && python main.py"
Write-Host "2. Start Frontend: cd frontend && npm start"
Write-Host "`nThe app will be available at http://localhost:3000" -ForegroundColor Green
