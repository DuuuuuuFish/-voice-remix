@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo [1/7] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
  echo Python not found. Please install Python 3.10+ and try again.
  exit /b 1
)

echo [2/7] Checking Node.js...
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js not found. Please install Node.js 20+ and try again.
  exit /b 1
)

echo [3/7] Preparing backend virtual environment...
if not exist "backend\.venv\Scripts\python.exe" (
  python -m venv backend\.venv
)

echo [4/7] Installing backend dependencies...
call backend\.venv\Scripts\activate.bat
python -m pip install --upgrade pip wheel
python -m pip install setuptools==69.5.1
pip install -r backend\requirements.txt
python -m pip install tiktoken==0.12.0
deactivate

echo [5/7] Installing frontend dependencies...
where npm >nul 2>nul
if errorlevel 1 (
  if defined VOICE_CLONE_NODE if defined VOICE_CLONE_PNPM_CJS (
    pushd frontend
    "%VOICE_CLONE_NODE%" "%VOICE_CLONE_PNPM_CJS%" install
    popd
  ) else if defined VOICE_CLONE_PNPM (
    pushd frontend
    call "%VOICE_CLONE_PNPM%" install
    popd
  ) else (
    echo npm not found. Please install a standard Node.js distribution that includes npm, or set VOICE_CLONE_PNPM / VOICE_CLONE_NODE + VOICE_CLONE_PNPM_CJS.
    exit /b 1
  )
) else (
  pushd frontend
  call npm install
  popd
)

echo [6/7] Creating required directories...
if not exist "backend\storage\uploads" mkdir "backend\storage\uploads"
if not exist "backend\storage\generated" mkdir "backend\storage\generated"
if not exist "backend\storage\voices" mkdir "backend\storage\voices"
if not exist "backend\pretrained_models" mkdir "backend\pretrained_models"
if not exist "logs" mkdir "logs"

echo [7/7] Initializing database...
call backend\.venv\Scripts\activate.bat
pushd backend
python -c "from app.main import create_app; create_app(); print('database initialized')"
popd
deactivate

echo Installation completed.
exit /b 0
