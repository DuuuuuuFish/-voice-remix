@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

if not exist "logs" mkdir "logs"

if not exist "backend\.venv\Scripts\python.exe" (
  echo Backend virtual environment not found. Running install.bat first...
  call install.bat
  if errorlevel 1 exit /b 1
)

set API_HOST=0.0.0.0
set API_PORT=8000
set FRONTEND_PORT=3000
set NEXT_PUBLIC_API_BASE_URL=http://localhost:%API_PORT%/api

if exist ".env" (
  for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
    if /I "%%A"=="API_HOST" set API_HOST=%%B
    if /I "%%A"=="API_PORT" set API_PORT=%%B
    if /I "%%A"=="FRONTEND_PORT" set FRONTEND_PORT=%%B
    if /I "%%A"=="NEXT_PUBLIC_API_BASE_URL" set NEXT_PUBLIC_API_BASE_URL=%%B
  )
)

echo Starting backend on %API_HOST%:%API_PORT% ...
start "voice-clone-backend" /min cmd /c "cd /d %~dp0backend && set API_HOST=%API_HOST%&& set API_PORT=%API_PORT%&& ..\backend\.venv\Scripts\python.exe -m uvicorn main:app --host %API_HOST% --port %API_PORT%"

echo Starting frontend on %FRONTEND_PORT% ...
where npm >nul 2>nul
if errorlevel 1 (
  where node >nul 2>nul
  if not errorlevel 1 (
    start "voice-clone-frontend" /min cmd /c "set FRONTEND_PORT=%FRONTEND_PORT%&& set NEXT_PUBLIC_API_BASE_URL=%NEXT_PUBLIC_API_BASE_URL%&& cd /d %~dp0frontend && node run-dev.cjs"
  ) else if defined VOICE_CLONE_NODE (
    start "voice-clone-frontend" /min cmd /c "set FRONTEND_PORT=%FRONTEND_PORT%&& set NEXT_PUBLIC_API_BASE_URL=%NEXT_PUBLIC_API_BASE_URL%&& cd /d %~dp0frontend && \"%VOICE_CLONE_NODE%\" run-dev.cjs"
  ) else if defined VOICE_CLONE_PNPM (
    start "voice-clone-frontend" /min cmd /c "set FRONTEND_PORT=%FRONTEND_PORT%&& set NEXT_PUBLIC_API_BASE_URL=%NEXT_PUBLIC_API_BASE_URL%&& cd /d %~dp0frontend && call \"%VOICE_CLONE_PNPM%\" dev"
  ) else (
    echo npm not found, and Node.js runtime fallback is unavailable. Please install Node.js or set VOICE_CLONE_NODE / VOICE_CLONE_PNPM and rerun start.bat.
    exit /b 1
  )
  goto frontend_done
)
start "voice-clone-frontend" /min cmd /c "set FRONTEND_PORT=%FRONTEND_PORT%&& set NEXT_PUBLIC_API_BASE_URL=%NEXT_PUBLIC_API_BASE_URL%&& cd /d %~dp0frontend && npm run dev"
:frontend_done

timeout /t 15 /nobreak >nul
start "" "http://localhost:%FRONTEND_PORT%"
exit /b 0
