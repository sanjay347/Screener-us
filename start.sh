#!/bin/bash
echo "Starting US Stock Screener backend..."
cd "$(dirname "$0")/backend"
export PATH="$PATH:/Users/sanjay/Library/Python/3.9/bin"
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
