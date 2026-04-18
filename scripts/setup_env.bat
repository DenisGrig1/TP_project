@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ENV_NAME=data_sem2"
set "PYTHON_VERSION=3.10"
set "SCRIPT_DIR=%~dp0"

echo [INFO] Starting environment setup...
echo [INFO] Environment name: %ENV_NAME%
echo [INFO] Python version: %PYTHON_VERSION%

cd /d "%SCRIPT_DIR%\.."

call :find_conda
if errorlevel 1 goto :fail

call :ensure_env
if errorlevel 1 goto :fail

call :install_requirements
if errorlevel 1 goto :fail

call :run_smoke
if errorlevel 1 goto :fail

echo.
echo [OK] Environment "%ENV_NAME%" is ready and smoke test passed!
set "EXIT_CODE=0"
goto :finish

:find_conda
echo [INFO] Looking for conda...
set "CONDA_BAT="

if exist "%USERPROFILE%\miniconda3\condabin\conda.bat" (
    set "CONDA_BAT=%USERPROFILE%\miniconda3\condabin\conda.bat"
) else if exist "%USERPROFILE%\anaconda3\condabin\conda.bat" (
    set "CONDA_BAT=%USERPROFILE%\anaconda3\condabin\conda.bat"
) else if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
    set "CONDA_BAT=%USERPROFILE%\miniconda3\Scripts\conda.exe"
) else if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" (
    set "CONDA_BAT=%USERPROFILE%\anaconda3\Scripts\conda.exe"
) else (
    where conda.bat >nul 2>nul
    if not errorlevel 1 (
        for /f "delims=" %%i in ('where conda.bat') do set "CONDA_BAT=%%i"
    ) else (
        where conda >nul 2>nul
        if not errorlevel 1 (
            for /f "delims=" %%i in ('where conda') do set "CONDA_BAT=%%i"
        )
    )
)

if "%CONDA_BAT%"=="" (
    echo [ERROR] Conda not found
    exit /b 1
)

echo [INFO] Conda found: %CONDA_BAT%
exit /b 0

:ensure_env
echo [INFO] Checking environment "%ENV_NAME%"...

call "%CONDA_BAT%" env list | findstr /C:"%ENV_NAME%" >nul
if errorlevel 1 (
    echo [INFO] Environment "%ENV_NAME%" not found. Creating...
    call "%CONDA_BAT%" create -n "%ENV_NAME%" python=%PYTHON_VERSION% -y
    if errorlevel 1 (
        echo [ERROR] Failed to create environment
        exit /b 1
    )
    echo [INFO] Environment created successfully
) else (
    echo [INFO] Environment "%ENV_NAME%" already exists
)
exit /b 0

:install_requirements
echo [INFO] Installing requirements from requirements.txt...

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found
    exit /b 1
)

call "%CONDA_BAT%" run -n "%ENV_NAME%" python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install requirements
    exit /b 1
)
echo [INFO] Requirements installed successfully
exit /b 0

:run_smoke
echo [INFO] Running smoke test...

if not exist "broken_env.py" (
    echo [ERROR] broken_env.py not found
    exit /b 1
)

call "%CONDA_BAT%" run -n "%ENV_NAME%" python broken_env.py
if errorlevel 1 (
    echo [ERROR] Smoke test failed
    exit /b 1
)
echo [INFO] Smoke test passed
exit /b 0

:fail
echo [ERROR] Setup failed!
set "EXIT_CODE=1"
goto :finish

:finish
echo.
if not "%NO_PAUSE%"=="1" (
    echo Press any key to close...
    pause >nul
)
exit /b %EXIT_CODE%