#!/bin/bash
echo "=== ForensicAI Frontend Setup ==="
cd "$(dirname "$0")/frontend"
echo "Installing npm packages..."
npm install
echo "Starting React dev server on http://localhost:3000 ..."
npm start
