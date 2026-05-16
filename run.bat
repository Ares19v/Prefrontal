@echo off
title Prefrontal — Dev Servers
color 0A

echo.
echo  ============================================================
echo   PREFRONTAL — Starting Development Environment
echo  ============================================================
echo.

:: Check venv exists
if not exist "backend\venv\Scripts\activate.bat" (
    echo  [ERROR] Virtual environment not found.
    echo  Run install.bat first.
    echo.
    pause
    exit /b 1
)

:: Check node_modules exists
if not exist "frontend\node_modules" (
    echo  [ERROR] Frontend dependencies not found.
    echo  Run install.bat first.
    echo.
    pause
    exit /b 1
)

echo  [1/2] Starting FastAPI backend on http://localhost:8000 ...
start "Prefrontal Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && echo Backend ready. && uvicorn main:app --reload --port 8000 --host 127.0.0.1"

:: Small delay so backend starts loading the embedding model first
timeout /t 3 /nobreak >nul

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
echo  Press any key to open the app in your browser...
pause >nul

start "" "http://localhost:3000"
