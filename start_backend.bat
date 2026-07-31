@echo off
echo === ForensicAI Backend Setup ===
cd /d "%~dp0backend"

if not exist "venv" (
  echo Creating virtual environment...
  python -m venv venv
)

call venv\Scripts\activate
echo Installing dependencies...
pip install -r requirements.txt -q

echo Starting Flask server on http://localhost:5000 ...
python app.py
pause
