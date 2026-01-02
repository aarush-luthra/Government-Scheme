"""
PDF Loader for Government Scheme Documents

Loads PDFs from the pdfs directory and extracts text with metadata.
"""

import os
from pathlib import Path
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


class PDFLoader:
    """Loads PDF files from a directory and extracts text content."""
    
    def __init__(self, pdf_dir: str = None):
        """
        Initialize the PDF loader.
        
        Args:
            pdf_dir: Path to directory containing PDFs. 
                     Defaults to backend/data/raw/pdfs/
        """
        if pdf_dir is None:
            base_dir = Path(__file__).resolve().parents[2]
            self.pdf_dir = base_dir / "backend" / "data" / "raw" / "pdfs"
        else:
            self.pdf_dir = Path(pdf_dir)
        
        if not self.pdf_dir.exists():
            self.pdf_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created PDF directory: {self.pdf_dir}")
    
    def get_pdf_files(self) -> List[Path]:
        """Get all PDF files in the directory."""
        return list(self.pdf_dir.glob("*.pdf"))
    
    def load_pdf(self, pdf_path: Path) -> List[Document]:
        """
        Load a single PDF and return documents with metadata.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of Document objects, one per page
        """
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()
        
        # Enhance metadata for each page
        filename = pdf_path.stem  # filename without extension
        for i, page in enumerate(pages):
            page.metadata.update({
                "source": "pdf",
                "filename": pdf_path.name,
                "title": filename,  # Required for VectorStore compatibility
                "category": "PDF Document",
                "department": "Unknown",
                "url": "",
                "page": page.metadata.get("page", i)
            })
        
        return pages
    
    def load_all_pdfs(self) -> List[Document]:
        """
        Load all PDFs from the directory.
        
        Returns:
            List of all Document objects from all PDFs
        """
        all_documents = []
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            print(f"No PDF files found in {self.pdf_dir}")
            return all_documents
        
        print(f"Found {len(pdf_files)} PDF file(s)")
        
        for pdf_path in pdf_files:
            try:
                print(f"  Loading: {pdf_path.name}")
                docs = self.load_pdf(pdf_path)
                all_documents.extend(docs)
                print(f"    → Extracted {len(docs)} page(s)")
            except Exception as e:
                print(f"  ✗ Error loading {pdf_path.name}: {e}")
        
        print(f"Total documents loaded: {len(all_documents)}")
        return all_documents


if __name__ == "__main__":
    # Test the loader
    loader = PDFLoader()
    docs = loader.load_all_pdfs()
    
    if docs:
        print("\nSample document:")
        print(f"  Content (first 200 chars): {docs[0].page_content[:200]}...")
        print(f"  Metadata: {docs[0].metadata}")
