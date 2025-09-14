@echo on
setlocal enabledelayedexpansion

REM Save home directory
set "HOME=%cd%"

REM ========== Start Python Backend ==========
cd /d "%HOME%\python-back"
echo.
echo ### Starting Python Backend ###
if not exist logs mkdir logs
start "" /d "%cd%" /b "python" music_lister.py ..\database\database.json > logs\music_lister.log 2>&1
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python*" /fo list ^| findstr "PID:"') do set PYTHON_BACK_PID=%%a
echo %PYTHON_BACK_PID%
cd /d "%HOME%"

REM ========== Start Express Backend ==========
cd /d "%HOME%\back"
echo.
echo ### Starting Express Backend ###
if exist logs rmdir /s /q logs
if not exist logs mkdir logs
if exist node_modules rmdir /s /q node_modules
call npm i --package-lock-only --omit=dev
call npm ci --omit=dev
start "" /d "%cd%" /b "node" server.js > logs\express-backend.log 2>&1
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq node.exe" /fo list ^| findstr "PID:"') do set BACKEND_PID=%%a
echo %BACKEND_PID%
cd /d "%HOME%"

REM ========== Start Vue Frontend ==========
cd /d "%HOME%\front"
echo.
echo ### Starting Vue Frontend ###
if exist logs rmdir /s /q logs
if not exist logs mkdir logs
rmdir /s /q node_modules
call npm i --package-lock-only --omit=dev
call npm ci --omit=dev
start "" /d "%cd%" /b "npm" run dev > logs\vue-frontend.log 2>&1
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq node.exe" /fo list ^| findstr "PID:"') do set FRONTEND_PID=%%a
echo %FRONTEND_PID%
cd /d "%HOME%"

REM ========== Start Browser ==========
start "" http://localhost:5173/


REM ========== Wait for CTRL+C ==========
echo.
echo All services started. Press key 'x' to kill them.
:waitloop
set command=
set /p "command=Enter command: "
if NOT "%command%"=="x" (
    goto waitloop
)

REM ================== CLEANUP HANDLER ==================
echo.
echo Stopping processes...

echo Stopping frontend (PID %FRONTEND_PID%)...
taskkill /PID %FRONTEND_PID% /F /T

echo Stopping backend (PID %BACKEND_PID%)...
taskkill /PID %BACKEND_PID% /F /T

echo Stopping python backend (PID %PYTHON_BACK_PID%)...
taskkill /PID %PYTHON_BACK_PID% /F /T

echo Kill remaining NodeJS processes...
:onemoreprocess
set REMAINING_NODE_PID=
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq node.exe" /fo list ^| findstr "PID:"') do set REMAINING_NODE_PID=%%a
if NOT "%REMAINING_NODE_PID%"=="" (
    taskkill /PID %REMAINING_NODE_PID% /F /T
    goto onemoreprocess
)

echo Exiting program.
@REM exit /b 0
