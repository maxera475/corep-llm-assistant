"""
Text chunking module for splitting documents into manageable pieces.
Creates chunks of 400-600 tokens with metadata preservation.
"""

import re
from typing import List, Dict
import tiktoken


class TextChunker:
    """Chunks text into token-sized pieces with overlap."""
    
    def __init__(self, 
                 min_chunk_size: int = 400,
                 max_chunk_size: int = 600,
                 overlap: int = 50):
        """
        Initialize the text chunker.
        
        Args:
            min_chunk_size: Minimum tokens per chunk
            max_chunk_size: Maximum tokens per chunk
            overlap: Number of overlapping tokens between chunks
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        
        # Initialize tokenizer (using cl100k_base for OpenAI models)
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Chunk a list of documents.
        
        Args:
            documents: List of document dictionaries with 'text' and 'metadata'
            
        Returns:
            List of chunked documents with preserved metadata
        """
        all_chunks = []
        
        for doc in documents:
            chunks = self._chunk_single_document(doc)
            all_chunks.extend(chunks)
            
        print(f"Created {len(all_chunks)} chunks from {len(documents)} documents")
        return all_chunks
    
    def _chunk_single_document(self, document: Dict) -> List[Dict]:
        """
        Chunk a single document into smaller pieces.
        
        Args:
            document: Document dictionary
            
        Returns:
            List of chunk dictionaries
        """
        text = document["text"]
        metadata = document["metadata"]
        
        # Split into sentences for better chunking
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = len(self.tokenizer.encode(sentence))
            
            # If adding this sentence exceeds max, save current chunk
            if current_tokens + sentence_tokens > self.max_chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                if current_tokens >= self.min_chunk_size:
                    chunks.append(self._create_chunk(chunk_text, metadata, len(chunks)))
                    
                    # Keep overlap sentences for context
                    overlap_text = chunk_text.split()[-self.overlap:]
                    current_chunk = [" ".join(overlap_text)]
                    current_tokens = len(self.tokenizer.encode(current_chunk[0]))
                else:
                    current_chunk = []
                    current_tokens = 0
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if current_tokens >= self.min_chunk_size or not chunks:
                chunks.append(self._create_chunk(chunk_text, metadata, len(chunks)))
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
        """
        # Simple sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _create_chunk(self, text: str, original_metadata: Dict, chunk_index: int) -> Dict:
        """
        Create a chunk dictionary with metadata.
        
        Args:
            text: Chunk text
            original_metadata: Metadata from original document
            chunk_index: Index of this chunk
            
        Returns:
            Chunk dictionary
        """
        return {
            "text": text,
            "metadata": {
                **original_metadata,
                "chunk_index": chunk_index,
                "chunk_tokens": len(self.tokenizer.encode(text))
            }
        }


def chunk_documents(documents: List[Dict], 
                   min_size: int = 400,
                   max_size: int = 600) -> List[Dict]:
    """
    Convenience function to chunk documents.
    
    Args:
        documents: List of documents
        min_size: Minimum chunk size
        max_size: Maximum chunk size
        
    Returns:
        List of chunks
    """
    chunker = TextChunker(min_chunk_size=min_size, max_chunk_size=max_size)
    return chunker.chunk_documents(documents)


if __name__ == "__main__":
    # Test the chunker
    from loader import load_documents
    
    input_path = r"C:\Users\Arpan\OneDrive\Desktop\prototype\Input_files"
    docs = load_documents(input_path)
    
    if docs:
        chunks = chunk_documents(docs)
        
        print(f"\nSample chunk:")
        print(f"Source: {chunks[0]['metadata']['source_file']}")
        print(f"Page: {chunks[0]['metadata']['page']}")
        print(f"Chunk index: {chunks[0]['metadata']['chunk_index']}")
        print(f"Tokens: {chunks[0]['metadata']['chunk_tokens']}")
        print(f"Text preview: {chunks[0]['text'][:300]}...")
