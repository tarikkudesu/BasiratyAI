# BasiratyAPI Setup Guide

## Quick Start

### First Time Setup

Run the setup script to initialize the environment and start the API:

```powershell
.\setup_and_run.ps1
```

This will:

1. Check Python installation
2. Create a virtual environment
3. Install all dependencies
4. Run the API server

### Subsequent Runs

After the first setup, you can use the quick run script:

```powershell
.\run.ps1
```

## Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Virtual Environment

```powershell
python -m venv venv
```

### 2. Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Run the API

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Access the API

Once running, the API will be available at:

- **API Endpoint**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Requirements

- Python 3.8 or higher
- Windows OS (for PowerShell scripts)
- Internet connection (for initial dependency download)

## Troubleshooting

### PowerShell Execution Policy Error

If you get an error about script execution being disabled, run PowerShell as Administrator and execute:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Not Found

Make sure Python is installed and added to your PATH. Download from:
https://www.python.org/downloads/

### Port Already in Use

If port 8000 is already in use, modify the port in the run scripts:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Stopping the Server

Press `Ctrl+C` in the terminal to stop the server.
