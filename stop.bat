@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set API_PORT=8000
set FRONTEND_PORT=3000
if exist ".env" (
  for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    if /I "%%A"=="API_PORT" set API_PORT=%%B
    if /I "%%A"=="FRONTEND_PORT" set FRONTEND_PORT=%%B
  )
)

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%P /F >nul 2>nul
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%API_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%P /F >nul 2>nul

taskkill /FI "WINDOWTITLE eq voice-clone-backend*" /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq voice-clone-frontend*" /F >nul 2>nul

echo Frontend and backend processes stopped.
exit /b 0
