"""
Configuration settings for COREP Assistant.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR.parent / "Input_files"
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"
AUDIT_LOG_DIR = BASE_DIR / "audit_logs"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)
AUDIT_LOG_DIR.mkdir(exist_ok=True)

# Google Gemini settings
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))

# Embedding settings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHUNK_MIN_SIZE = int(os.getenv("CHUNK_MIN_SIZE", "400"))
CHUNK_MAX_SIZE = int(os.getenv("CHUNK_MAX_SIZE", "600"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Retrieval settings
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Streamlit settings
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# Template settings
DEFAULT_TEMPLATE = "C01.00"

# Validation settings
ENABLE_VALIDATION = os.getenv("ENABLE_VALIDATION", "true").lower() == "true"

# Audit settings
ENABLE_AUDIT_LOGGING = os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true"


def get_config() -> dict:
    """Get all configuration as dictionary."""
    return {
        "base_dir": str(BASE_DIR),
        "input_dir": str(INPUT_DIR),
        "data_dir": str(DATA_DIR),
        "export_dir": str(EXPORT_DIR),
        "audit_log_dir": str(AUDIT_LOG_DIR),
        "gemini": {
            "api_key_set": bool(GOOGLE_API_KEY),
            "model": GEMINI_MODEL,
            "temperature": GEMINI_TEMPERATURE
        },
        "embedding": {
            "model": EMBEDDING_MODEL,
            "chunk_min_size": CHUNK_MIN_SIZE,
            "chunk_max_size": CHUNK_MAX_SIZE,
            "chunk_overlap": CHUNK_OVERLAP
        },
        "retrieval": {
            "default_top_k": DEFAULT_TOP_K
        },
        "api": {
            "host": API_HOST,
            "port": API_PORT
        },
        "validation_enabled": ENABLE_VALIDATION,
        "audit_logging_enabled": ENABLE_AUDIT_LOGGING
    }


if __name__ == "__main__":
    import json
    config = get_config()
    print("Current Configuration:")
    print(json.dumps(config, indent=2))
