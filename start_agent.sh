#!/bin/bash

echo "========================================"
echo " PETER GRIFFIN MOLTBOOK AGENT"
echo "========================================"
echo

cd "$(dirname "$0")"

if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please run setup_agent.py first to register your agent."
    echo
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo
echo "Starting Peter Griffin Agent..."
echo "Press Ctrl+C to stop the agent"
echo

python src/main.py
