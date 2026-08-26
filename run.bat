@echo off
title Prefrontal — Dev Servers
color 0A

echo.
echo  ============================================================
echo   PREFRONTAL — Starting Development Environment
echo  ============================================================
echo.

:: Check venv exists
:: Virtual environment check bypassed (using system Python if venv absent)

:: Check node_modules exists
if not exist "frontend\node_modules" (
    echo  [ERROR] Frontend dependencies not found.
    echo  Run install.bat first.
    echo.
    pause
    exit /b 1
)

echo  [1/2] Starting FastAPI backend on http://localhost:8000 ...
start "Prefrontal Backend" cmd /k "cd /d %~dp0backend && if exist venv\Scripts\activate call venv\Scripts\activate && echo Backend ready. && uvicorn main:app --reload --port 8000 --host 127.0.0.1"

:: Small delay so backend starts loading the embedding model first
ping 127.0.0.1 -n 6 >nul

echo  [2/2] Starting Next.js frontend on http://localhost:3000 ...
start "Prefrontal Frontend" cmd /k "cd /d %~dp0frontend && echo Frontend ready. && npm run dev"

echo.
echo  ============================================================
echo   Both servers are starting in separate windows.
echo.
echo   Backend : http://localhost:8000/api/health
echo   Frontend: http://localhost:3000
echo  ============================================================
echo.
echo  Opening the app in your browser...
ping 127.0.0.1 -n 3 >nul

start "" "http://localhost:3000"
