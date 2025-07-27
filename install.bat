@echo off
echo 🚀 Setting up Paper Search Interface...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📚 Installing dependencies...
pip install -r requirements.txt

echo ✅ Installation complete!
echo.
echo 🎉 To start the application:
echo    venv\Scripts\activate.bat
echo    python run.py
echo.
echo 🌐 Then open your browser to: http://localhost:5001
pause 