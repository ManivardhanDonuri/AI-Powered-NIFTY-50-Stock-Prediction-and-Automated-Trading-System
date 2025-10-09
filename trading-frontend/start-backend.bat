@echo off
echo Starting Trading API Backend Server...

cd api
echo Installing dependencies...
call npm install

echo.
echo Starting server on port 8000...
echo API will be available at: http://localhost:8000
echo WebSocket will be available at: http://localhost:8000
echo.

node server.js