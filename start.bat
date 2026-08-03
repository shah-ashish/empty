@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo  Starting Kaggle Local LLM Proxy Pipeline
echo ==========================================

echo === Step 1: Checking / Creating Virtual Environment ===
if not exist "venv" (
    echo [VENV] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    if !errorlevel! equ 0 (
        echo [VENV] SUCCESS: Virtual environment 'venv' created successfully.
    ) else (
        echo [VENV] FAILURE: Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo [VENV] SUCCESS: Virtual environment 'venv' already exists.
)

:: Activate venv
call venv\Scripts\activate.bat
if !errorlevel! equ 0 (
    echo [VENV] SUCCESS: Virtual environment activated.
) else (
    echo [VENV] FAILURE: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo === Step 2: Installing Dependencies ===
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
if !errorlevel! equ 0 (
    echo [Dependencies] SUCCESS: All Python packages installed successfully.
) else (
    echo [Dependencies] FAILURE: Failed to install Python dependencies from requirements.txt.
    pause
    exit /b 1
)

echo === Step 3: Checking System Tools ===
:: Check Ollama
where ollama >nul 2>nul
if !errorlevel! neq 0 (
    echo [Ollama] FAILURE: Ollama was not found in PATH! Download and install it from https://ollama.com/download/windows
    pause
    exit /b 1
) else (
    echo [Ollama] SUCCESS: Ollama CLI is available.
)

:: Check bore CLI
where bore >nul 2>nul
if !errorlevel! neq 0 (
    if not exist "bore.exe" (
        echo [Tunnel] Downloading bore CLI for Windows...
        powershell -Command "Invoke-WebRequest -Uri 'https://github.com/ekzhang/bore/releases/download/v0.6.0/bore-v0.6.0-x86_64-pc-windows-msvc.zip' -OutFile 'bore.zip'"
        powershell -Command "Expand-Archive -Path 'bore.zip' -DestinationPath '.' -Force"
        del bore.zip
        if exist "bore.exe" (
            echo [Tunnel] SUCCESS: bore.exe downloaded successfully.
        ) else (
            echo [Tunnel] FAILURE: Failed to download bore.exe.
            pause
            exit /b 1
        )
    ) else (
        echo [Tunnel] SUCCESS: bore.exe is present in the workspace directory.
    )
) else (
    echo [Tunnel] SUCCESS: bore CLI is available in system PATH.
)

echo === Step 4: Starting Main Python Application ===
python main.py
if !errorlevel! neq 0 (
    echo [System] FAILURE: main.py exited with an error.
    pause
    exit /b 1
)

pause
