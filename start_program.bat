@echo off
setlocal enabledelayedexpansion

REM Save home directory
set "HOME=%cd%"

REM ========== Start Python Backend ==========
cd /d "%HOME%\python-back"
echo.
echo ### Starting Python Backend ###
if not exist logs mkdir logs
@REM if not exist winvenv (
@REM     python -m venv winvenv
@REM )
@REM cmd /C windowsvenv\Scripts\activate.bat
@REM pip install -r requirements.txt
cmd /c python music_lister.py ..\database\database.json > logs\music_lister.log 2>&1
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /fo list ^| findstr "PID:"') do set @PYTHON_BACK_PID=%%a
ECHO %@PYTHON_BACK_PID%
@REM call windowsvenv\Scripts\deactivate.bat
cd /d "%HOME%"

REM ========== Start Express Backend ==========
cd /d "%HOME%\back"
echo.
echo ### Starting Express Backend ###
if not exist logs mkdir logs
if exist node_modules rmdir /s /q node_modules
npm i --package-lock-only --omit=dev
npm ci --omit=dev
call node server.js > logs\express-backend.log 2>&1
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq node.exe" /fo list ^| findstr "PID:"') do set @BACKEND_PID=%%a
echo %@BACKEND_PID%
cd /d "%HOME%"

REM ========== Start Vue Frontend ==========
cd /d "%HOME%\front"
echo.
echo ### Starting Vue Frontend ###
rmdir /s /q node_modules
npm i --package-lock-only --omit=dev
npm ci --omit=dev
call npm run dev
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq node.exe" /fo list ^| findstr "PID:"') do set @FRONTEND_PID=%%a
echo %@FRONTEND_PID%
cd /d "%HOME%"

@REM REM ========== Wait for CTRL+C ==========
@REM echo.
@REM echo All services started. Press CTRL+C to stop them.
@REM :waitloop
@REM timeout /t 2 >nul
@REM goto waitloop


@REM REM ================== CLEANUP HANDLER ==================
@REM :trap
@REM echo.
@REM echo SIGINT caught
@REM echo Stopping processes...

@REM if not "%PYTHON_BACK_PID%"=="" (
@REM     echo Stopping python backend (PID %PYTHON_BACK_PID%)...
@REM     taskkill /PID %PYTHON_BACK_PID% /F >nul 2>&1
@REM )

@REM if not "%BACKEND_PID%"=="" (
@REM     echo Stopping backend (PID %BACKEND_PID%)...
@REM     taskkill /PID %BACKEND_PID% /F >nul 2>&1
@REM )

@REM if not "%FRONTEND_PID%"=="" (
@REM     echo Stopping frontend (PID %FRONTEND_PID%)...
@REM     taskkill /PID %FRONTEND_PID% /F >nul 2>&1
@REM )

@REM echo Exiting program.
@REM exit /b 0
