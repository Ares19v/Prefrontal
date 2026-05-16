@echo off
title Prefrontal — Install
color 0E

echo.
echo  ============================================================
echo   PREFRONTAL — Installing All Dependencies
echo  ============================================================
echo.

:: ── Step 1: Python version check ────────────────────────────────
echo  [1/5] Checking Python version...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] Python not found. Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo         Found Python %PYVER%

:: ── Step 2: Create virtual environment ──────────────────────────
echo.
echo  [2/5] Creating Python virtual environment...
if exist "backend\venv" (
    echo         venv already exists, skipping creation.
) else (
    python -m venv backend\venv
    if %ERRORLEVEL% NEQ 0 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo         Created backend\venv
)

:: ── Step 3: Install Python dependencies ─────────────────────────
echo.
echo  [3/5] Installing Python dependencies (this may take a few minutes)...
call backend\venv\Scripts\activate
pip install --upgrade pip -q
pip install -r backend\requirements.txt

:: Install langchain-groq explicitly (may not be in requirements.txt)
pip install langchain-groq -q

if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] pip install failed. Check error output above.
    pause
    exit /b 1
)
echo         Python dependencies installed.

:: ── Step 4: Install Node.js dependencies ────────────────────────
echo.
echo  [4/5] Installing Node.js frontend dependencies...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [WARN] Node.js not found. Install from https://nodejs.org
    echo         Skipping frontend install.
    goto STEP5
)

cd frontend
npm install
if %ERRORLEVEL% NEQ 0 (
    echo  [ERROR] npm install failed.
    cd ..
    pause
    exit /b 1
)
cd ..
echo         Node.js dependencies installed.

:STEP5
:: ── Step 5: Verify .env ─────────────────────────────────────────
echo.
echo  [5/5] Checking backend\.env ...
if not exist "backend\.env" (
    echo  [WARN] backend\.env not found.
    echo         Create it with your GROQ_API_KEY and PINECONE_API_KEY.
    echo         See backend\.env.example for the template.
) else (
    echo         backend\.env found.
)

echo.
echo  ============================================================
echo   Installation complete!
echo.
echo   Next steps:
echo     1. Double-click run.bat to start the app
echo     2. Double-click test.bat to verify everything works
echo  ============================================================
echo.
pause
