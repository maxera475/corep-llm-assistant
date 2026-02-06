# COREP Assistant - Deployment Guide

Complete guide for deploying the COREP Regulatory Reporting Assistant to production.

---

## 🎯 Deployment Options

1. **Streamlit Cloud** (Easiest, Free)
2. **Google Cloud Run** (Scalable, Pay-as-you-go)
3. **AWS EC2** (Full Control)
4. **Azure App Service** (Enterprise)
5. **Docker + Any Cloud** (Portable)
6. **Local Server** (On-premises)

---

## 📦 Option 1: Streamlit Cloud (Recommended for Quick Deploy)

### Prerequisites
- GitHub account
- Google Gemini API key
- PDF files accessible (commit or use external storage)

### Step 1: Prepare Repository

```bash
# 1. Initialize git repository
cd C:\Users\Arpan\OneDrive\Desktop\prototype\corep_assistant
git init

# 2. Create .gitignore (already exists)

# 3. Add files
git add .
git commit -m "Initial commit - COREP Assistant"

# 4. Create GitHub repository (on GitHub.com)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/corep-assistant.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud

1. **Go to**: https://share.streamlit.io/

2. **Sign in** with GitHub

3. **New app**:
   - Repository: `YOUR_USERNAME/corep-assistant`
   - Branch: `main`
   - Main file path: `app.py`

4. **Advanced settings** → Secrets:
   ```toml
   GOOGLE_API_KEY = "your_actual_gemini_api_key_here"
   ```

5. **Deploy!**

### Step 3: Handle Data Files

**Option A: Build index on first run** (if PDFs in repo)
- Keep PDFs in repo (if < 100MB total)
- Index builds automatically on startup

**Option B: Pre-build and upload** (recommended)
```bash
# Build locally
python -m ingestion.embedder

# Add to repo
git add data/
git commit -m "Add pre-built index"
git push
```

**Option C: Use external storage**
- Upload PDFs to Google Cloud Storage/S3
- Modify `loader.py` to download from cloud
- Less ideal for prototype

### Limitations
- 1 GB RAM limit
- Can timeout on large processing
- Best for pre-built indexes

---

## 🐳 Option 2: Docker Deployment (Universal)

### Step 1: Create Dockerfile

```dockerfile
# Create: Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Build FAISS index (optional - can do at runtime)
# RUN python -m ingestion.embedder

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 2: Create docker-compose.yml

```yaml
# Create: docker-compose.yml
version: '3.8'

services:
  corep-assistant:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./exports:/app/exports
      - ./audit_logs:/app/audit_logs
    restart: unless-stopped
```

### Step 3: Create .dockerignore

```
# Create: .dockerignore
.git
.gitignore
__pycache__
*.pyc
*.pyo
*.pyd
.env
venv/
env/
*.log
.vscode/
.idea/
data/
exports/
audit_logs/
```

### Step 4: Build and Run

```bash
# Build image
docker build -t corep-assistant .

# Run container
docker run -d \
  -p 8501:8501 \
  -e GOOGLE_API_KEY="your_key_here" \
  -v $(pwd)/data:/app/data \
  --name corep-assistant \
  corep-assistant

# Or use docker-compose
docker-compose up -d

# View logs
docker logs -f corep-assistant
```

### Step 5: Access
- Open: http://localhost:8501

---

## ☁️ Option 3: Google Cloud Run (Scalable)

### Prerequisites
- Google Cloud account
- `gcloud` CLI installed

### Step 1: Setup GCP

```bash
# Install gcloud CLI
# Windows: https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### Step 2: Create cloudbuild.yaml

```yaml
# Create: cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/corep-assistant', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/corep-assistant']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'corep-assistant'
      - '--image=gcr.io/$PROJECT_ID/corep-assistant'
      - '--platform=managed'
      - '--region=us-central1'
      - '--allow-unauthenticated'
      - '--memory=2Gi'
      - '--cpu=2'
      - '--set-env-vars=GOOGLE_API_KEY=${_GOOGLE_API_KEY}'
```

### Step 3: Deploy

```bash
# Build and deploy
gcloud builds submit --config cloudbuild.yaml \
  --substitutions _GOOGLE_API_KEY="your_key_here"

# Or manual deploy
gcloud run deploy corep-assistant \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars GOOGLE_API_KEY="your_key_here"
```

### Step 4: Get URL

```bash
gcloud run services describe corep-assistant \
  --region us-central1 \
  --format 'value(status.url)'
```

### Pricing
- Pay per request
- Free tier: 2 million requests/month
- ~$0.00002400 per request after

---

## 🖥️ Option 4: AWS EC2 (Traditional)

### Step 1: Launch EC2 Instance

1. **AWS Console** → EC2 → Launch Instance
2. **Choose:**
   - Ubuntu 22.04 LTS
   - t3.medium (2 vCPU, 4GB RAM minimum)
   - 20GB storage
   - Security group: Allow ports 22, 8501, 80, 443

### Step 2: Connect and Setup

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# Install git
sudo apt install -y git

# Clone repository
git clone https://github.com/YOUR_USERNAME/corep-assistant.git
cd corep-assistant
```

### Step 3: Setup Application

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Add: GOOGLE_API_KEY=your_key_here

# Build FAISS index
python -m ingestion.embedder
```

### Step 4: Setup Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/corep-assistant.service
```

```ini
[Unit]
Description=COREP Regulatory Reporting Assistant
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/corep-assistant
Environment="PATH=/home/ubuntu/corep-assistant/venv/bin"
ExecStart=/home/ubuntu/corep-assistant/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable corep-assistant
sudo systemctl start corep-assistant

# Check status
sudo systemctl status corep-assistant
```

### Step 5: Setup Nginx (Optional)

```bash
# Install Nginx
sudo apt install -y nginx

# Configure
sudo nano /etc/nginx/sites-available/corep-assistant
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/corep-assistant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Setup SSL (Optional)

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

---

## 🔷 Option 5: Azure App Service

### Step 1: Install Azure CLI

```bash
# Windows
winget install Microsoft.AzureCLI

# Login
az login
```

### Step 2: Create Resources

```bash
# Create resource group
az group create --name corep-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name corep-plan \
  --resource-group corep-rg \
  --sku B2 \
  --is-linux

# Create web app
az webapp create \
  --resource-group corep-rg \
  --plan corep-plan \
  --name corep-assistant \
  --runtime "PYTHON:3.11" \
  --deployment-container-image-name python:3.11
```

### Step 3: Configure

```bash
# Set environment variables
az webapp config appsettings set \
  --resource-group corep-rg \
  --name corep-assistant \
  --settings GOOGLE_API_KEY="your_key_here"

# Deploy
az webapp up \
  --resource-group corep-rg \
  --name corep-assistant \
  --runtime "PYTHON:3.11"
```

---

## 🏠 Option 6: Local/On-Premises Server

### Windows Server

```powershell
# Install Python 3.11
winget install Python.Python.3.11

# Clone repository
git clone https://github.com/YOUR_USERNAME/corep-assistant.git
cd corep-assistant

# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Create .env
echo GOOGLE_API_KEY=your_key_here > .env

# Build index
python -m ingestion.embedder

# Run as Windows service using NSSM
# Download: https://nssm.cc/download
nssm install COREPAssistant "C:\path\to\venv\Scripts\streamlit.exe" "run app.py --server.port=8501"
nssm start COREPAssistant
```

### Linux Server (Ubuntu/Debian)

Follow AWS EC2 steps above (Step 2-4)

---

## 🔐 Security Best Practices

### 1. Environment Variables

Never commit `.env` file. Use platform-specific secrets:

**Streamlit Cloud**: Secrets UI
**Docker**: Environment variables or secrets
**Cloud Run**: Secret Manager
**EC2**: AWS Secrets Manager
**Azure**: Key Vault

### 2. API Key Rotation

```python
# Implement key rotation in config.py
import time

def get_api_key():
    # Check if key needs rotation
    # Fetch from secrets manager
    pass
```

### 3. Network Security

- Use HTTPS only (SSL/TLS)
- Implement firewall rules
- Enable rate limiting
- Use VPC/private networks

### 4. Authentication

Add authentication to Streamlit:

```python
# Add to app.py
import streamlit as st

def check_password():
    """Returns True if user has correct password."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()
```

---

## 📊 Monitoring & Logging

### 1. Application Logs

```python
# Add to config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Health Check Endpoint

```python
# Add to api.py or create health.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### 3. Monitoring Tools

- **Streamlit**: Built-in analytics
- **Cloud Run**: Cloud Monitoring
- **AWS**: CloudWatch
- **Self-hosted**: Prometheus + Grafana

---

## 🚀 Performance Optimization

### 1. Pre-build FAISS Index

Always commit pre-built index to repo:
```bash
python -m ingestion.embedder
git add data/
git commit -m "Add FAISS index"
```

### 2. Caching

Already implemented with `@st.cache_resource` in app.py

### 3. Resource Limits

Set appropriate limits:
- **CPU**: 2-4 cores
- **RAM**: 2-4 GB
- **Storage**: 10-20 GB

### 4. Database for Audit Logs (Optional)

Replace file-based logging with PostgreSQL/MongoDB

---

## 💰 Cost Estimates

### Streamlit Cloud
- **Free tier**: 1 app, community support
- **Pro**: $99/month per developer

### Google Cloud Run
- **Free tier**: 2M requests/month
- **After**: ~$50-200/month (moderate usage)

### AWS EC2
- **t3.medium**: ~$30/month
- **+ Storage**: ~$2/month
- **+ Data transfer**: varies

### Azure App Service
- **B2 tier**: ~$75/month

### Self-hosted
- **Server**: Own hardware
- **Electricity**: varies
- **Maintenance**: time cost

---

## 🧪 Testing Deployment

### Pre-deployment Checklist

```bash
# 1. Test locally
streamlit run app.py

# 2. Test with production-like data
python -m ingestion.embedder

# 3. Run validation
python -m pytest tests/ (if you add tests)

# 4. Check environment variables
python config.py

# 5. Test API endpoints
curl http://localhost:8000/health
```

### Post-deployment Testing

1. **Access URL** and verify app loads
2. **Test query** with sample scenario
3. **Check exports** (Excel, JSON, audit logs)
4. **Monitor logs** for errors
5. **Test under load** (optional: Apache Bench, JMeter)

---

## 🔄 CI/CD Pipeline

### GitHub Actions Example

```yaml
# Create: .github/workflows/deploy.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v0
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
      
      - name: Build and Deploy
        run: |
          gcloud builds submit --config cloudbuild.yaml
```

---

## 📱 Quick Deploy Commands

### Streamlit Cloud
```bash
# Just push to GitHub and deploy via UI
git push origin main
```

### Docker
```bash
docker build -t corep-assistant . && docker run -p 8501:8501 corep-assistant
```

### Google Cloud Run
```bash
gcloud run deploy corep-assistant --source . --region us-central1
```

### AWS ECR + ECS
```bash
aws ecr create-repository --repository-name corep-assistant
docker tag corep-assistant:latest AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/corep-assistant
docker push AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/corep-assistant
```

---

## 🆘 Troubleshooting

### Issue: Out of Memory
**Solution**: Increase RAM or optimize embeddings

### Issue: Slow Cold Starts
**Solution**: Use pre-built index, warm instances

### Issue: API Key Not Found
**Solution**: Check environment variables/secrets

### Issue: FAISS Index Not Loading
**Solution**: Ensure `data/` directory exists and has correct files

### Issue: Port Already in Use
**Solution**: Change port or kill existing process

---

## ✅ Deployment Success Checklist

- [ ] Application runs without errors
- [ ] FAISS index is accessible
- [ ] API key is configured securely
- [ ] HTTPS/SSL is enabled (production)
- [ ] Health check endpoint works
- [ ] Logs are being generated
- [ ] Monitoring is set up
- [ ] Backups configured (audit logs, exports)
- [ ] Authentication enabled (if required)
- [ ] Documentation updated with deployment URL
- [ ] Team notified of new deployment

---

## 🎉 You're Live!

Once deployed, your COREP Assistant will be accessible at:
- **Streamlit Cloud**: `https://your-app.streamlit.app`
- **Cloud Run**: `https://corep-assistant-xxx-uc.a.run.app`
- **EC2**: `http://your-ec2-ip:8501` or `https://your-domain.com`
- **Azure**: `https://corep-assistant.azurewebsites.net`

Share the URL with users and start analyzing COREP scenarios! 🚀
