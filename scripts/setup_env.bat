@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "ENV_NAME=data_sem2"
set "PYTHON_VERSION=3.10"

cd /d "%SCRIPT_DIR%\.."

call :find_conda
if errorlevel 1 goto :fail

call :ensure_env
if errorlevel 1 goto :fail

call :install_requirements
if errorlevel 1 goto :fail

call :run_smoke
if errorlevel 1 goto :fail

echo [OK] Environment "%ENV_NAME%" is ready.
goto :ok

:find_conda
rem TODO: set CONDA_BAT=...
exit /b 0

:ensure_env
rem TODO: conda env list + conda create
exit /b 0

:install_requirements
rem TODO: conda run -n ... python -m pip install -r requirements.txt
exit /b 0

:run_smoke
rem TODO: conda run -n ... python broken_env.py
exit /b 0

:fail
echo [ERROR] Setup failed.
set "EXIT_CODE=1"
goto :finish

:ok
set "EXIT_CODE=0"
goto :finish

:finish
echo.
if not "%NO_PAUSE%"=="1" (
  echo Press any key to close...
  pause >nul
)
exit /b %EXIT_CODE%
