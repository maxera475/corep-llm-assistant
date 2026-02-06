"""
Auto-initialization for Streamlit Cloud deployment.
Builds FAISS index on first run if not found.
"""

import streamlit as st
from pathlib import Path
import sys
import subprocess


def check_and_build_index():
    """
    Check if FAISS index exists, build if missing.
    Returns: (success: bool, message: str)
    """
    index_path = Path("data/index.faiss")
    metadata_path = Path("data/metadata.pkl")
    input_dir = Path("../Input_files")
    
    # Check if index exists
    if index_path.exists() and metadata_path.exists():
        return True, "Index found"
    
    # Check if input files exist
    if not input_dir.exists() or not list(input_dir.glob("*.pdf")):
        return False, f"""
        **Missing Input Files**
        
        No PDF files found in `Input_files/` directory.
        
        Please ensure:
        1. PDF documents are in the `Input_files/` folder
        2. The folder is committed to your repository
        """
    
    # Build index
    st.warning("⏳ Building FAISS index... This may take 5-10 minutes on first run.")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("Loading documents...")
        progress_bar.progress(25)
        
        # Import here to avoid circular imports
        from ingestion.embedder import build_index
        
        status_text.text("Generating embeddings...")
        progress_bar.progress(50)
        
        # Build the index
        build_index(str(input_dir), "data")
        
        status_text.text("Finalizing...")
        progress_bar.progress(100)
        
        st.success("✅ Index built successfully!")
        return True, "Index built"
        
    except Exception as e:
        return False, f"""
        **Index Build Failed**
        
        Error: {str(e)}
        
        This may happen due to:
        - Insufficient memory on Streamlit Cloud (1GB limit)
        - Missing or corrupted PDF files
        - API rate limits
        
        **Solution:** Build index locally and commit to repository.
        """


def ensure_api_key():
    """
    Check if Google API key is configured.
    Returns: (configured: bool, message: str)
    """
    import os
    
    # Check environment variable
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # Check Streamlit secrets
    if not api_key:
        try:
            api_key = st.secrets.get("GOOGLE_API_KEY")
        except:
            pass
    
    if not api_key or api_key == "your_google_api_key_here":
        return False, """
        **Google API Key Not Configured**
        
        For Streamlit Cloud:
        1. Go to your app settings
        2. Click "Secrets"
        3. Add: `GOOGLE_API_KEY = "your_actual_key"`
        
        Get your free API key: https://makersuite.google.com/app/apikey
        """
    
    return True, "API key configured"


def initialize_app():
    """
    Initialize application with all checks.
    Returns: (ready: bool, message: str)
    """
    # Check API key
    api_ready, api_msg = ensure_api_key()
    if not api_ready:
        return False, api_msg
    
    # Check and build index
    index_ready, index_msg = check_and_build_index()
    if not index_ready:
        return False, index_msg
    
    return True, "System ready"
