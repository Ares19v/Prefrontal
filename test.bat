@echo off
title Prefrontal — Test Suite
color 0B

echo.
echo  ============================================================
echo   PREFRONTAL — Running System Tests
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
call backend\venv\Scripts\activate && python scripts\test_all.py

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
