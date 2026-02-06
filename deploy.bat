@echo off
REM COREP Assistant - Quick Deployment Script for Windows

echo ==========================================
echo   COREP Assistant - Deployment Helper
echo ==========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo Error: .env file not found
    echo Please create .env file with GOOGLE_API_KEY
    pause
    exit /b 1
)

REM Check if data/index.faiss exists
if not exist "data\index.faiss" (
    echo Warning: FAISS index not found
    echo Building index... This may take 5-10 minutes
    python -m ingestion.embedder
)

echo.
echo Select deployment platform:
echo 1) Docker (Local)
echo 2) Docker Compose (Local)
echo 3) Test Locally
echo 4) Streamlit Cloud (Instructions)
echo 5) Exit
echo.

set /p choice="Enter choice [1-5]: "

if "%choice%"=="1" goto docker
if "%choice%"=="2" goto compose
if "%choice%"=="3" goto local
if "%choice%"=="4" goto streamlit
if "%choice%"=="5" goto end
goto invalid

:docker
echo Building Docker image...
docker build -t corep-assistant .

echo Running container...
docker run -d --name corep-assistant -p 8501:8501 --env-file .env -v %cd%\data:/app/data -v %cd%\exports:/app/exports -v %cd%\audit_logs:/app/audit_logs corep-assistant

echo.
echo Successfully Deployed!
echo Access at: http://localhost:8501
echo.
echo View logs: docker logs -f corep-assistant
echo Stop: docker stop corep-assistant
pause
goto end

:compose
echo Starting with Docker Compose...
docker-compose up -d

echo.
echo Successfully Deployed!
echo Access at: http://localhost:8501
echo.
echo View logs: docker-compose logs -f
echo Stop: docker-compose down
pause
goto end

:local
echo Testing locally...
streamlit run app.py
goto end

:streamlit
echo.
echo Streamlit Cloud Deployment (Manual Steps):
echo.
echo 1. Push code to GitHub:
echo    git init
echo    git add .
echo    git commit -m "Initial commit"
echo    git remote add origin https://github.com/USERNAME/REPO.git
echo    git push -u origin main
echo.
echo 2. Go to: https://share.streamlit.io/
echo.
echo 3. Connect your GitHub repository
echo.
echo 4. Set these secrets in Streamlit Cloud:
echo    GOOGLE_API_KEY = your_actual_key_here
echo.
echo 5. Deploy!
echo.
pause
goto end

:invalid
echo Invalid choice
pause
goto end

:end
