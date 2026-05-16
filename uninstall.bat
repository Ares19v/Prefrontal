@echo off
title Prefrontal — Uninstall
color 04

echo.
echo  ============================================================
echo   PREFRONTAL — Uninstall
echo  ============================================================
echo.
echo  This will remove:
echo    - backend\venv     (Python virtual environment)
echo    - frontend\node_modules  (Node.js packages)
echo    - frontend\.next   (Build cache)
echo.
echo  Your source code, .env, and knowledge_base will NOT be deleted.
echo.

set /p CONFIRM=  Type YES to continue: 
if /i not "%CONFIRM%"=="YES" (
    echo  Cancelled.
    pause
    exit /b 0
)

echo.

:: ── Remove Python venv ───────────────────────────────────────────
echo  [1/3] Removing backend\venv...
if exist "backend\venv" (
    rmdir /s /q "backend\venv"
    echo         Removed.
) else (
    echo         Not found, skipping.
)

:: ── Remove node_modules ──────────────────────────────────────────
echo  [2/3] Removing frontend\node_modules...
if exist "frontend\node_modules" (
    rmdir /s /q "frontend\node_modules"
    echo         Removed.
) else (
    echo         Not found, skipping.
)

:: ── Remove Next.js build cache ───────────────────────────────────
echo  [3/3] Removing frontend\.next build cache...
if exist "frontend\.next" (
    rmdir /s /q "frontend\.next"
    echo         Removed.
) else (
    echo         Not found, skipping.
)

echo.
echo  ============================================================
echo   Uninstall complete.
echo   Run install.bat to reinstall everything from scratch.
echo  ============================================================
echo.
pause
