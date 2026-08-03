#!/bin/bash
echo "=== ForensicAI Backend Setup ==="
cd "$(dirname "$0")/backend"

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

source venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt -q

echo "Starting Flask server on http://localhost:5000 ..."
python app.py
