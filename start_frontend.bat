@echo off
echo === ForensicAI Frontend Setup ===
cd /d "%~dp0frontend"
echo Installing npm packages...
npm install
echo Starting React dev server on http://localhost:3000 ...
npm start
pause
