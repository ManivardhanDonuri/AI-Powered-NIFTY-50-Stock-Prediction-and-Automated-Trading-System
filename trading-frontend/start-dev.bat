@echo off
echo Starting Trading System Development Environment...

echo.
echo Installing API dependencies...
cd api
call npm install
if %errorlevel% neq 0 (
    echo Failed to install API dependencies
    pause
    exit /b 1
)

echo.
echo Starting API server...
start "API Server" cmd /k "npm run dev"

echo.
echo Waiting for API server to start...
timeout /t 3 /nobreak > nul

cd ..
echo.
echo Installing frontend dependencies...
call npm install
if %errorlevel% neq 0 (
    echo Failed to install frontend dependencies
    pause
    exit /b 1
)

echo.
echo Starting frontend development server...
start "Frontend" cmd /k "npm run dev"

echo.
echo Development environment started!
echo API Server: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul