# BasiratyAPI Setup and Run Script
# This script initializes the Python environment and runs the API

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BasiratyAPI Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCheck) {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "  Please install Python 3.8 or higher from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Create virtual environment if it doesn't exist
Write-Host ""
Write-Host "[2/5] Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    Write-Host "  Creating new virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Failed to create virtual environment!" -ForegroundColor Red
        exit 1
    }
    Write-Host "  Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/5] Activating virtual environment..." -ForegroundColor Yellow
$activateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "  Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "  Activation script not found!" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "[4/5] Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    Write-Host "  Installing packages from requirements.txt..." -ForegroundColor Cyan
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
    Write-Host "  Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "  requirements.txt not found!" -ForegroundColor Red
    exit 1
}

# Check if model file exists
Write-Host ""
Write-Host "[5/5] Checking model file..." -ForegroundColor Yellow
if (Test-Path "yolov8n.pt") {
    Write-Host "  YOLOv8 model file found" -ForegroundColor Green
} else {
    Write-Host "  yolov8n.pt not found - it will be downloaded on first run" -ForegroundColor Yellow
}

# Run the API
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting BasiratyAPI Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Green
Write-Host "  - http://localhost:8000" -ForegroundColor White
Write-Host "  - http://localhost:8000/docs (API Documentation)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the FastAPI application with uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
