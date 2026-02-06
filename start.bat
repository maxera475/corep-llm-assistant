@echo off
REM Quick start script for COREP Assistant on Windows

echo ========================================
echo COREP Regulatory Reporting Assistant
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install dependencies
echo Installing dependencies...
pip install -q -r requirements.txt
echo.

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo *** IMPORTANT ***
    echo Please edit .env file and add your Google Gemini API key
    echo.
    pause
)

REM Check if index exists
if not exist "data\index.faiss" (
    echo FAISS index not found. Building index...
    echo This may take several minutes...
    python -m ingestion.embedder
    echo.
)

REM Start Streamlit app
echo Starting Streamlit application...
echo.
streamlit run app.py

pause
