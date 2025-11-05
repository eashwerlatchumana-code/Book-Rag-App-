#!/bin/bash
# Startup script for RAG Chat Backend API (Linux/macOS)

echo "Starting RAG Chat Backend API..."
echo "================================"
echo ""

# Activate virtual environment
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found!"
    echo "Please run: python -m venv .venv"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found!"
    echo "Please create a .env file with your API keys"
    echo ""
fi

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

python main.py
