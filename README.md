# COREP Regulatory Reporting Assistant

LLM-assisted prototype for COREP regulatory reporting with RAG-based rule retrieval.

## Setup Instructions

### 1. Prerequisites
- Python 3.11+
- Google Gemini API key

### 2. Installation

```bash
# Navigate to project directory
cd corep_assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

**Important:** You need your own Google Gemini API key. This is free to get!

1. **Get your API key:**
   - Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Click "Create API Key"
   - Copy your key

2. **Configure the app:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Windows:
   copy .env.example .env
   ```

3. **Edit `.env` and add your key:**
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

⚠️ **Security Note:** Never commit `.env` to git - it's already in `.gitignore`

### 4. Initialize the System

Run the ingestion pipeline to process PDFs and build the FAISS index:

```bash
python -m ingestion.embedder
```

This will:
- Load all PDFs from Input_files/
- Extract and chunk text
- Generate embeddings
- Save FAISS index to data/

### 5. Run the Application

**Option A: Streamlit Frontend (Recommended)**
```bash
streamlit run app.py
```
Open browser at http://localhost:8501

**Option B: FastAPI Backend**
```bash
uvicorn api:app --reload
```
API docs at http://localhost:8000/docs

## Usage

### Streamlit Interface:
1. Enter your question (e.g., "How should share premium be classified?")
2. Provide scenario description with numbers
3. Click "Run Assistant"
4. Review the filled template, validation results, and audit trail
5. Download Excel file

### Example Scenario:
```
Bank has:
- Share capital: €10,000,000
- Share premium: €2,000,000
- Retained earnings: €5,000,000
- Intangible assets: €500,000
```

### Example Question:
```
How should these items be classified in the C01.00 Own Funds template?
```

## Project Structure

```
corep_assistant/
├── app.py                  # Streamlit frontend
├── api.py                  # FastAPI backend
├── requirements.txt
├── .env
│
├── ingestion/
│   ├── loader.py          # PDF loading
│   ├── chunker.py         # Text chunking
│   └── embedder.py        # Embedding generation
│
├── rag/
│   └── retriever.py       # Vector search
│
├── llm/
│   ├── prompts.py         # Prompt templates
│   └── reasoner.py        # LLM reasoning
│
├── templates/
│   └── mapper.py          # Excel template mapping
│
├── validation/
│   └── rules.py           # Validation engine
│
├── audit/
│   └── logger.py          # Audit trail
│
└── data/
    ├── index.faiss        # FAISS vector index
    └── metadata.pkl       # Chunk metadata
```

## Notes

- This is a prototype for demonstration purposes
- Not intended for production use
- Validate all outputs manually
- LLM responses may vary
