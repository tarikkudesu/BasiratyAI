# BasiratyAPI Quick Run Script
# Use this after the first setup

Write-Host "Starting BasiratyAPI Server..." -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup_and_run.ps1 first to initialize the environment" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Server will be available at:" -ForegroundColor Green
Write-Host "  - http://localhost:8000" -ForegroundColor White
Write-Host "  - http://localhost:8000/docs (API Documentation)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Run the FastAPI application
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
