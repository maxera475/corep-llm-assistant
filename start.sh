#!/bin/bash
# Quick start script for COREP Assistant on Linux/Mac

echo "========================================"
echo "COREP Regulatory Reporting Assistant"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "*** IMPORTANT ***"
    echo "Please edit .env file and add your Google Gemini API key"
    echo ""
    read -p "Press enter to continue..."
fi

# Check if index exists
if [ ! -f "data/index.faiss" ]; then
    echo "FAISS index not found. Building index..."
    echo "This may take several minutes..."
    python -m ingestion.embedder
    echo ""
fi

# Start Streamlit app
echo "Starting Streamlit application..."
echo ""
streamlit run app.py
