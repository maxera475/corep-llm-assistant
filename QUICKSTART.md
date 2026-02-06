# COREP Assistant - Quick Start Guide

## 🚀 Quick Start (Windows)

1. **Double-click `start.bat`**
   
   This will:
   - Create virtual environment
   - Install dependencies
   - Build the FAISS index
   - Start the Streamlit app

2. **Add your OpenAI API key** to `.env` file when prompted

3. **Wait for index building** (first time only, ~5-10 minutes)

4. **Access the app** at http://localhost:8501

## 🚀 Quick Start (Linux/Mac)

```bash
chmod +x start.sh
./start.sh
```

## 📋 Manual Setup

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create `.env` file:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Build FAISS Index

```bash
python -m ingestion.embedder
```

This processes all PDFs in `Input_files/` directory.

### 5. Run Application

**Option A: Streamlit (Recommended)**
```bash
streamlit run app.py
```
Access at: http://localhost:8501

**Option B: FastAPI**
```bash
uvicorn api:app --reload
```
API docs at: http://localhost:8000/docs

## 📁 Project Structure

```
corep_assistant/
├── app.py                  # Streamlit frontend
├── api.py                  # FastAPI backend
├── config.py              # Configuration
├── setup.py               # Setup script
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (create this)
│
├── ingestion/            # Document processing
│   ├── loader.py         # PDF loading
│   ├── chunker.py        # Text chunking
│   └── embedder.py       # Embedding generation
│
├── rag/                  # Retrieval
│   └── retriever.py      # Vector search
│
├── llm/                  # LLM reasoning
│   ├── prompts.py        # Prompt templates
│   └── reasoner.py       # LLM calls
│
├── templates/            # Template mapping
│   └── mapper.py         # Excel export
│
├── validation/           # Validation
│   └── rules.py          # Validation rules
│
├── audit/               # Audit logging
│   └── logger.py        # Audit trail
│
└── data/                # Generated files
    ├── index.faiss      # Vector index
    └── metadata.pkl     # Metadata
```

## 🎯 Usage Example

### In Streamlit:

1. **Enter Question:**
   ```
   How should these items be classified in the C01.00 Own Funds template?
   ```

2. **Provide Scenario:**
   ```
   Bank XYZ has:
   - Ordinary share capital: €10,000,000
   - Share premium: €2,000,000
   - Retained earnings: €5,000,000
   - Other reserves: €1,500,000
   - Intangible assets: €500,000
   - Deferred tax assets: €300,000
   ```

3. **Click "Run Analysis"**

4. **Review Results:**
   - Summary table with classifications
   - Template view
   - Validation messages
   - Retrieved rules
   - Audit trail

5. **Export:**
   - Download Excel report
   - Download audit log
   - Download analysis JSON

## 🔧 Configuration

Edit `.env` file to customize:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.1
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_MIN_SIZE=400
CHUNK_MAX_SIZE=600
DEFAULT_TOP_K=5
```

## 🐛 Troubleshooting

### "FAISS index not found"
```bash
python -m ingestion.embedder
```

### "OpenAI API key not found"
Add key to `.env` file:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### "No PDF files found"
Ensure PDFs are in:
```
C:\Users\Arpan\OneDrive\Desktop\prototype\Input_files\
```

### Import errors
```bash
pip install -r requirements.txt
```

### Port already in use
Change port in config or:
```bash
streamlit run app.py --server.port 8502
```

## 📊 Testing Components

### Test document loading:
```bash
python -m ingestion.loader
```

### Test retriever:
```bash
python -m rag.retriever
```

### Test mapper:
```bash
python -m templates.mapper
```

### Test validation:
```bash
python -m validation.rules
```

## 🔐 Security Notes

- **Never commit** `.env` file with real API keys
- Keep `.env` in `.gitignore`
- API keys are loaded from environment variables
- Audit logs contain sensitive data - store securely

## 📝 Notes

- **Prototype**: Not for production use
- **LLM outputs**: Always validate manually
- **Processing time**: First run builds index (~5-10 min)
- **Subsequent runs**: Fast (~30-60 seconds)
- **Token usage**: ~2000-5000 tokens per query

## 🆘 Support

For issues:
1. Check troubleshooting section above
2. Review logs in `audit_logs/`
3. Run setup script: `python setup.py`
4. Check configuration: `python config.py`

## ✅ Success Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured with API key
- [ ] PDF files in Input_files directory
- [ ] FAISS index built successfully
- [ ] Application starts without errors
- [ ] Can run analysis and get results

## 🎉 You're Ready!

Once all checklist items are complete, you can:
- Run `streamlit run app.py`
- Open browser to http://localhost:8501
- Start analyzing COREP scenarios!
