"""
Embedding generation and FAISS index creation.
Processes documents, generates embeddings, and stores in vector database.
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from ingestion.loader import load_documents
from ingestion.chunker import chunk_documents


class EmbeddingPipeline:
    """Creates embeddings and builds FAISS index."""
    
    def __init__(self, 
                 model_name: str = "all-MiniLM-L6-v2",
                 data_dir: str = "data"):
        """
        Initialize the embedding pipeline.
        
        Args:
            model_name: SentenceTransformer model name
            data_dir: Directory to save index and metadata
        """
        self.model_name = model_name
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully")
        
        self.index_path = self.data_dir / "index.faiss"
        self.metadata_path = self.data_dir / "metadata.pkl"
        
    def build_index_from_pdfs(self, input_dir: str) -> None:
        """
        Complete pipeline: load PDFs, chunk, embed, and build index.
        
        Args:
            input_dir: Directory containing PDF files
        """
        print("\n=== Starting Document Ingestion Pipeline ===\n")
        
        # Step 1: Load documents
        print("Step 1: Loading PDF documents...")
        documents = load_documents(input_dir)
        
        if not documents:
            print("No documents loaded. Exiting.")
            return
        
        # Step 2: Chunk documents
        print("\nStep 2: Chunking documents...")
        chunks = chunk_documents(documents)
        
        if not chunks:
            print("No chunks created. Exiting.")
            return
        
        # Step 3: Generate embeddings
        print("\nStep 3: Generating embeddings...")
        embeddings = self._generate_embeddings(chunks)
        
        # Step 4: Build FAISS index
        print("\nStep 4: Building FAISS index...")
        self._build_faiss_index(embeddings, chunks)
        
        print("\n=== Pipeline Complete ===")
        print(f"Index saved to: {self.index_path}")
        print(f"Metadata saved to: {self.metadata_path}")
        
    def _generate_embeddings(self, chunks: List[Dict]) -> np.ndarray:
        """
        Generate embeddings for all chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Numpy array of embeddings
        """
        texts = [chunk["text"] for chunk in chunks]
        
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True
        )
        
        print(f"Embeddings shape: {embeddings.shape}")
        return embeddings
    
    def _build_faiss_index(self, embeddings: np.ndarray, chunks: List[Dict]) -> None:
        """
        Build and save FAISS index.
        
        Args:
            embeddings: Embedding vectors
            chunks: Chunk dictionaries
        """
        dimension = embeddings.shape[1]
        
        # Create FAISS index (L2 distance)
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        # Save index
        faiss.write_index(index, str(self.index_path))
        print(f"FAISS index created with {index.ntotal} vectors")
        
        # Save metadata
        metadata = [chunk["metadata"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        
        data_to_save = {
            "chunks": chunks,
            "texts": texts,
            "metadata": metadata,
            "model_name": self.model_name
        }
        
        with open(self.metadata_path, "wb") as f:
            pickle.dump(data_to_save, f)
        
        print(f"Metadata saved: {len(metadata)} entries")


def build_index(input_dir: str, data_dir: str = "data") -> None:
    """
    Convenience function to build index.
    
    Args:
        input_dir: Directory with PDF files
        data_dir: Directory to save index
    """
    pipeline = EmbeddingPipeline(data_dir=data_dir)
    pipeline.build_index_from_pdfs(input_dir)


if __name__ == "__main__":
    # Run the complete pipeline
    input_directory = r"C:\Users\Arpan\OneDrive\Desktop\prototype\Input_files"
    output_directory = "data"
    
    print("Starting embedding pipeline...")
    print(f"Input directory: {input_directory}")
    print(f"Output directory: {output_directory}\n")
    
    build_index(input_directory, output_directory)
    
    print("\n✓ Embedding pipeline completed successfully!")
