"""
Setup script to initialize the COREP Assistant.
Checks dependencies, creates directories, and runs initial setup.
"""

import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_env_file():
    """Check if .env file exists."""
    print("\nChecking .env configuration...")
    
    env_path = Path(".env")
    env_example = Path(".env.example")
    
    if not env_path.exists():
        if env_example.exists():
            print("⚠️  .env file not found. Creating from .env.example...")
            env_example.read_text()
            with open(env_path, "w") as f:
                f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            print("✓ Created .env file - PLEASE ADD YOUR OPENAI API KEY")
            return False
        else:
            print("❌ .env file not found")
            return False
    
    # Check if API key is set
    env_content = env_path.read_text()
    if "your_google_api_key_here" in env_content or "GOOGLE_API_KEY=" not in env_content:
        print("⚠️  Google Gemini API key not configured in .env file")
        return False
    
    print("✓ .env file configured")
    return True


def create_directories():
    """Create necessary directories."""
    print("\nCreating directories...")
    
    directories = [
        "data",
        "exports",
        "audit_logs"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"✓ {dir_name}/")
    
    return True


def check_input_files():
    """Check if input PDF files exist."""
    print("\nChecking input files...")
    
    input_dir = Path("../Input_files")
    
    if not input_dir.exists():
        print(f"⚠️  Input directory not found: {input_dir}")
        print("   Please ensure PDF files are in: C:\\Users\\Arpan\\OneDrive\\Desktop\\prototype\\Input_files\\")
        return False
    
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in {input_dir}")
        return False
    
    print(f"✓ Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files[:5]:  # Show first 5
        print(f"  - {pdf.name}")
    
    if len(pdf_files) > 5:
        print(f"  ... and {len(pdf_files) - 5} more")
    
    return True


def check_index_exists():
    """Check if FAISS index exists."""
    print("\nChecking FAISS index...")
    
    index_path = Path("data/index.faiss")
    metadata_path = Path("data/metadata.pkl")
    
    if index_path.exists() and metadata_path.exists():
        print("✓ FAISS index found")
        return True
    else:
        print("⚠️  FAISS index not found - needs to be built")
        return False


def run_embedding_pipeline():
    """Run the embedding pipeline."""
    print("\nRunning embedding pipeline...")
    print("This may take several minutes depending on the number of PDFs...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ingestion.embedder"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Embedding pipeline completed successfully")
            return True
        else:
            print(f"❌ Embedding pipeline failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running embedding pipeline: {e}")
        return False


def main():
    """Main setup function."""
    print_header("COREP Regulatory Reporting Assistant - Setup")
    
    # Track setup status
    all_ok = True
    needs_index = False
    
    # Step 1: Check Python version
    if not check_python_version():
        all_ok = False
    
    # Step 2: Check environment configuration
    if not check_env_file():
        all_ok = False
    
    # Step 3: Create directories
    if not create_directories():
        all_ok = False
    
    # Step 4: Check input files
    if not check_input_files():
        all_ok = False
    
    # Step 5: Check if index exists
    if not check_index_exists():
        needs_index = True
    
    # Summary
    print_header("Setup Summary")
    
    if not all_ok:
        print("⚠️  Setup incomplete. Please resolve the issues above.\n")
        print("Common fixes:")
        print("  1. Add your OpenAI API key to .env file")
        print("  2. Ensure PDF files are in Input_files directory")
        print("  3. Install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    if needs_index:
        print("✓ Configuration complete")
        print("\n⚠️  FAISS index needs to be built")
        print("\nNext step:")
        print("  Run: python -m ingestion.embedder")
        
        response = input("\nWould you like to build the index now? (y/n): ")
        
        if response.lower() == 'y':
            if run_embedding_pipeline():
                print("\n✅ Setup complete! You can now run the application:")
                print("   streamlit run app.py")
            else:
                print("\n⚠️  Index creation failed. Please run manually:")
                print("   python -m ingestion.embedder")
                sys.exit(1)
        else:
            print("\nPlease build the index before running the application:")
            print("  python -m ingestion.embedder")
    else:
        print("✅ Setup complete! Everything is ready.")
        print("\nYou can now run the application:")
        print("  streamlit run app.py")
        print("\nOr start the API server:")
        print("  uvicorn api:app --reload")


if __name__ == "__main__":
    main()
