#!/bin/bash

# COREP Assistant - Quick Deployment Script
# This script helps you deploy to different platforms

set -e

echo "=========================================="
echo "  COREP Assistant - Deployment Helper"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create .env file with GOOGLE_API_KEY"
    exit 1
fi

# Check if data/index.faiss exists
if [ ! -f "data/index.faiss" ]; then
    echo -e "${YELLOW}Warning: FAISS index not found${NC}"
    echo "Building index... This may take 5-10 minutes"
    python -m ingestion.embedder
fi

echo ""
echo "Select deployment platform:"
echo "1) Docker (Local)"
echo "2) Docker Compose (Local)"
echo "3) Google Cloud Run"
echo "4) Streamlit Cloud (Manual)"
echo "5) Test Locally"
echo "6) Exit"
echo ""

read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo -e "${GREEN}Building Docker image...${NC}"
        docker build -t corep-assistant .
        
        echo -e "${GREEN}Running container...${NC}"
        docker run -d \
            --name corep-assistant \
            -p 8501:8501 \
            --env-file .env \
            -v $(pwd)/data:/app/data \
            -v $(pwd)/exports:/app/exports \
            -v $(pwd)/audit_logs:/app/audit_logs \
            corep-assistant
        
        echo -e "${GREEN}✓ Deployed!${NC}"
        echo "Access at: http://localhost:8501"
        echo ""
        echo "View logs: docker logs -f corep-assistant"
        echo "Stop: docker stop corep-assistant"
        ;;
    
    2)
        echo -e "${GREEN}Starting with Docker Compose...${NC}"
        docker-compose up -d
        
        echo -e "${GREEN}✓ Deployed!${NC}"
        echo "Access at: http://localhost:8501"
        echo ""
        echo "View logs: docker-compose logs -f"
        echo "Stop: docker-compose down"
        ;;
    
    3)
        echo -e "${GREEN}Deploying to Google Cloud Run...${NC}"
        
        # Check if gcloud is installed
        if ! command -v gcloud &> /dev/null; then
            echo -e "${RED}Error: gcloud CLI not found${NC}"
            echo "Install from: https://cloud.google.com/sdk/docs/install"
            exit 1
        fi
        
        read -p "Enter GCP Project ID: " PROJECT_ID
        read -p "Enter region (default: us-central1): " REGION
        REGION=${REGION:-us-central1}
        
        gcloud config set project $PROJECT_ID
        
        echo "Building and deploying..."
        gcloud run deploy corep-assistant \
            --source . \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated \
            --memory 2Gi \
            --cpu 2 \
            --set-env-vars GOOGLE_API_KEY=$(grep GOOGLE_API_KEY .env | cut -d '=' -f2)
        
        SERVICE_URL=$(gcloud run services describe corep-assistant --region $REGION --format 'value(status.url)')
        echo -e "${GREEN}✓ Deployed!${NC}"
        echo "Access at: $SERVICE_URL"
        ;;
    
    4)
        echo -e "${YELLOW}Streamlit Cloud Deployment (Manual Steps):${NC}"
        echo ""
        echo "1. Push code to GitHub:"
        echo "   git init"
        echo "   git add ."
        echo "   git commit -m 'Initial commit'"
        echo "   git remote add origin https://github.com/USERNAME/REPO.git"
        echo "   git push -u origin main"
        echo ""
        echo "2. Go to: https://share.streamlit.io/"
        echo ""
        echo "3. Connect your GitHub repository"
        echo ""
        echo "4. Set these secrets in Streamlit Cloud:"
        echo "   GOOGLE_API_KEY = your_actual_key_here"
        echo ""
        echo "5. Deploy!"
        ;;
    
    5)
        echo -e "${GREEN}Testing locally...${NC}"
        streamlit run app.py
        ;;
    
    6)
        echo "Exiting..."
        exit 0
        ;;
    
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
