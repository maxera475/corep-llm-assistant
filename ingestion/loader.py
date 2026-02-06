"""
PDF document loader for COREP regulatory documents.
Extracts text from PDFs with metadata (page numbers, source files).
"""

import os
from typing import List, Dict
import pdfplumber
from pathlib import Path


class DocumentLoader:
    """Loads and extracts text from PDF files."""
    
    def __init__(self, input_dir: str):
        """
        Initialize the document loader.
        
        Args:
            input_dir: Path to directory containing PDF files
        """
        self.input_dir = Path(input_dir)
        
    def load_all_pdfs(self) -> List[Dict]:
        """
        Load all PDF files from the input directory.
        
        Returns:
            List of dictionaries containing text and metadata
        """
        documents = []
        
        if not self.input_dir.exists():
            print(f"Warning: Input directory {self.input_dir} does not exist")
            return documents
            
        pdf_files = list(self.input_dir.glob("*.pdf"))
        
        if not pdf_files:
            print(f"Warning: No PDF files found in {self.input_dir}")
            return documents
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_path in pdf_files:
            print(f"Loading: {pdf_path.name}")
            docs = self._load_single_pdf(pdf_path)
            documents.extend(docs)
            
        print(f"Total documents extracted: {len(documents)}")
        return documents
    
    def _load_single_pdf(self, pdf_path: Path) -> List[Dict]:
        """
        Load a single PDF file and extract text by page.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of document dictionaries
        """
        documents = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text()
                    
                    if text and text.strip():
                        doc = {
                            "text": text.strip(),
                            "metadata": {
                                "source_file": pdf_path.name,
                                "page": page_num,
                                "total_pages": len(pdf.pages)
                            }
                        }
                        documents.append(doc)
                        
        except Exception as e:
            print(f"Error loading {pdf_path.name}: {str(e)}")
            
        return documents


def load_documents(input_dir: str) -> List[Dict]:
    """
    Convenience function to load all documents.
    
    Args:
        input_dir: Path to input directory
        
    Returns:
        List of document dictionaries
    """
    loader = DocumentLoader(input_dir)
    return loader.load_all_pdfs()


if __name__ == "__main__":
    # Test the loader
    input_path = r"C:\Users\Arpan\OneDrive\Desktop\prototype\Input_files"
    docs = load_documents(input_path)
    
    if docs:
        print(f"\nSample document:")
        print(f"Source: {docs[0]['metadata']['source_file']}")
        print(f"Page: {docs[0]['metadata']['page']}")
        print(f"Text preview: {docs[0]['text'][:200]}...")
