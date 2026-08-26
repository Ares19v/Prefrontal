@echo off
title Prefrontal — Test Suite
color 0B

echo.
echo  ============================================================
echo   PREFRONTAL — Running System Tests
echo  ============================================================
echo.

:: Check venv exists
:: Virtual environment check bypassed (using system Python if venv absent)

:: Check test script exists
if not exist "scripts\test_all.py" (
    echo  [ERROR] Test script not found at scripts\test_all.py
    echo.
    pause
    exit /b 1
)

echo  NOTE: Make sure the backend is running (run.bat) for API tests.
echo        Tests 1-7 work without it. Test 8 requires it.
echo.
echo  Starting tests...
echo.

:: Run with UTF-8 so box-drawing chars display correctly
set PYTHONUTF8=1
if exist backend\venv\Scripts\activate call backend\venv\Scripts\activate && python scripts\test_all.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo  ============================================================
    echo   ALL TESTS PASSED — Prefrontal is ready.
    echo  ============================================================
) else (
    echo  ============================================================
    echo   SOME TESTS FAILED — Review output above.
    echo  ============================================================
)

echo.
pause
