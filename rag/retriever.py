"""
RAG retriever for semantic search over COREP regulatory documents.
Uses FAISS for vector similarity search.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Tuple
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class RAGRetriever:
    """Retrieves relevant document chunks using semantic search."""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the retriever.
        
        Args:
            data_dir: Directory containing FAISS index and metadata
        """
        self.data_dir = Path(data_dir)
        self.index_path = self.data_dir / "index.faiss"
        self.metadata_path = self.data_dir / "metadata.pkl"
        
        # Load index and metadata
        self._load_index()
        self._load_metadata()
        
    def _load_index(self) -> None:
        """Load FAISS index from disk."""
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {self.index_path}. "
                f"Please run the embedding pipeline first."
            )
        
        self.index = faiss.read_index(str(self.index_path))
        print(f"Loaded FAISS index with {self.index.ntotal} vectors")
        
    def _load_metadata(self) -> None:
        """Load metadata from disk."""
        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata not found at {self.metadata_path}. "
                f"Please run the embedding pipeline first."
            )
        
        with open(self.metadata_path, "rb") as f:
            data = pickle.load(f)
        
        self.chunks = data["chunks"]
        self.texts = data["texts"]
        self.metadata = data["metadata"]
        self.model_name = data["model_name"]
        
        print(f"Loaded {len(self.chunks)} chunks")
        
        # Load embedding model
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks for a query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of dictionaries with text, metadata, and similarity score
        """
        # Generate query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Prepare results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                result = {
                    "text": self.texts[idx],
                    "metadata": self.metadata[idx],
                    "similarity_score": float(distance),
                    "rank": len(results) + 1
                }
                results.append(result)
        
        return results
    
    def retrieve_with_context(self, 
                             query: str, 
                             top_k: int = 5,
                             include_summary: bool = True) -> Dict:
        """
        Retrieve chunks with additional context information.
        
        Args:
            query: Search query
            top_k: Number of results
            include_summary: Include summary statistics
            
        Returns:
            Dictionary with results and metadata
        """
        results = self.retrieve(query, top_k)
        
        response = {
            "query": query,
            "top_k": top_k,
            "results": results,
            "total_results": len(results)
        }
        
        if include_summary:
            # Add summary statistics
            sources = set(r["metadata"]["source_file"] for r in results)
            pages = set(r["metadata"]["page"] for r in results)
            
            response["summary"] = {
                "unique_sources": len(sources),
                "unique_pages": len(pages),
                "source_files": list(sources),
                "page_numbers": sorted(pages)
            }
        
        return response
    
    def format_for_llm(self, results: List[Dict]) -> str:
        """
        Format retrieved chunks for LLM consumption.
        
        Args:
            results: List of retrieval results
            
        Returns:
            Formatted string for LLM prompt
        """
        formatted_chunks = []
        
        for i, result in enumerate(results, 1):
            chunk_text = f"""
[CHUNK {i}]
Source: {result['metadata']['source_file']}
Page: {result['metadata']['page']}
Relevance Score: {result['similarity_score']:.4f}

Content:
{result['text']}

---
"""
            formatted_chunks.append(chunk_text)
        
        return "\n".join(formatted_chunks)


def retrieve_relevant_rules(query: str, top_k: int = 5, data_dir: str = "data") -> List[Dict]:
    """
    Convenience function to retrieve relevant rules.
    
    Args:
        query: Search query
        top_k: Number of results
        data_dir: Data directory
        
    Returns:
        List of retrieval results
    """
    retriever = RAGRetriever(data_dir=data_dir)
    return retriever.retrieve(query, top_k)


if __name__ == "__main__":
    # Test the retriever
    try:
        retriever = RAGRetriever(data_dir="data")
        
        # Test query
        query = "How should share premium be classified in own funds?"
        print(f"\nQuery: {query}\n")
        
        results = retriever.retrieve_with_context(query, top_k=3)
        
        print(f"Found {results['total_results']} results")
        print(f"\nSummary:")
        if "summary" in results:
            print(f"  - Sources: {results['summary']['unique_sources']}")
            print(f"  - Files: {results['summary']['source_files']}")
            print(f"  - Pages: {results['summary']['page_numbers']}")
        
        print(f"\nTop result:")
        top_result = results['results'][0]
        print(f"Source: {top_result['metadata']['source_file']}")
        print(f"Page: {top_result['metadata']['page']}")
        print(f"Score: {top_result['similarity_score']:.4f}")
        print(f"Text preview: {top_result['text'][:300]}...")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run the embedding pipeline first:")
        print("  python -m ingestion.embedder")
