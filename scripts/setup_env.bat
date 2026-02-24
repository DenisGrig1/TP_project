@echo off

REM Проверяем наличие Conda
for /f %%i in ('where anaconda-prompt') do set CONDA_PATH=%%~dpni
if not defined CONDA_PATH (
    echo Error: Anaconda Prompt not found!
    exit /b 1
)

REM Подключаем переменные среды Conda
call "%CONDA_PATH%\Scripts\activate.bat"

REM Получаем путь к файлу requirements.txt относительно текущего скрипта
set REQUIREMENTS_FILE=%~dp0requirements.txt
if not exist "%REQUIREMENTS_FILE%" (
    echo Error: Requirements file not found at %REQUIREMENTS_FILE%
    exit /b 1
)

REM Имя окружения и версия Python
set ENV_NAME=myenv
set PYTHON_VERSION=3.8

REM Создаем виртуальное окружение, если оно отсутствует
conda info --envs | findstr /C:"^%ENV_NAME%$" > nul || (
    echo Creating environment...
    call conda create -y -n %ENV_NAME% python=%PYTHON_VERSION%
)

REM Устанавливаем зависимости из requirements.txt
call conda activate %ENV_NAME%
pip install -r "%REQUIREMENTS_FILE%"

REM Запускаем тестовый скрипт
python "%~dp0broken_env.py"
if ERRORLEVEL 1 (
    echo Error occurred during smoke test.
    exit /b 1
) else (
    echo Smoke test passed successfully.
    exit /b 0
)
