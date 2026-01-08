"""
Extraction Cache

Caches LLM extraction results to avoid re-processing unchanged PDFs.
Uses content hashing for cache invalidation.
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ExtractionCache:
    """
    File-based cache for LLM extraction results.
    
    Each PDF's extraction is stored as:
    - {filename}.json: The extracted facts
    - {filename}.meta: Hash, timestamp, model info
    """
    
    def __init__(self, cache_dir: str):
        """
        Initialize the extraction cache.
        
        Args:
            cache_dir: Directory to store cached extractions
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"ExtractionCache initialized at {self.cache_dir}")
    
    def _get_file_hash(self, file_path: str) -> str:
        """Compute MD5 hash of file content."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _get_cache_paths(self, pdf_filename: str) -> Tuple[Path, Path]:
        """Get paths for cache data and metadata files."""
        base = self.cache_dir / pdf_filename
        return base.with_suffix('.json'), base.with_suffix('.meta')
    
    def is_cached(self, pdf_path: str) -> bool:
        """
        Check if a valid cache exists for the PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if cached and hash matches, False otherwise
        """
        pdf_filename = Path(pdf_path).name
        data_path, meta_path = self._get_cache_paths(pdf_filename)
        
        if not data_path.exists() or not meta_path.exists():
            return False
        
        try:
            with open(meta_path, 'r') as f:
                meta = json.load(f)
            
            current_hash = self._get_file_hash(pdf_path)
            if meta.get('content_hash') == current_hash:
                logger.debug(f"Cache hit for {pdf_filename}")
                return True
            else:
                logger.debug(f"Cache invalidated for {pdf_filename} (hash mismatch)")
                return False
                
        except Exception as e:
            logger.warning(f"Error reading cache metadata: {e}")
            return False
    
    def get_cached(self, pdf_path: str) -> Optional[List[Dict]]:
        """
        Retrieve cached extraction for a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of fact dictionaries, or None if not cached
        """
        if not self.is_cached(pdf_path):
            return None
        
        pdf_filename = Path(pdf_path).name
        data_path, _ = self._get_cache_paths(pdf_filename)
        
        try:
            with open(data_path, 'r') as f:
                facts = json.load(f)
            logger.info(f"Loaded {len(facts)} cached facts for {pdf_filename}")
            return facts
        except Exception as e:
            logger.error(f"Error loading cached data: {e}")
            return None
    
    def save_cache(
        self, 
        pdf_path: str, 
        facts: List[Dict],
        model: str = "unknown"
    ) -> bool:
        """
        Save extraction results to cache.
        
        Args:
            pdf_path: Path to the source PDF
            facts: List of extracted fact dictionaries
            model: LLM model used for extraction
            
        Returns:
            True if saved successfully, False otherwise
        """
        pdf_filename = Path(pdf_path).name
        data_path, meta_path = self._get_cache_paths(pdf_filename)
        
        try:
            # Prepare facts for serialization (ensure all values serializable)
            serializable_facts = []
            for fact in facts:
                serializable_facts.append({
                    "fact": str(fact.get("fact", "")),
                    "category": str(fact.get("category", "other")),
                    "confidence": str(fact.get("confidence", "medium")),
                    "page": fact.get("page", 0)
                })
            
            # Save extracted facts
            with open(data_path, 'w') as f:
                json.dump(serializable_facts, f, indent=2)
            
            # Save metadata
            meta = {
                "content_hash": self._get_file_hash(pdf_path),
                "extraction_timestamp": datetime.now().isoformat(),
                "llm_model": model,
                "fact_count": len(facts),
                "source_file": pdf_filename
            }
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)
            
            logger.info(f"Cached {len(facts)} facts for {pdf_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            return False
    
    def invalidate(self, pdf_path: str) -> bool:
        """
        Remove cached extraction for a PDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            True if removed, False if not found or error
        """
        pdf_filename = Path(pdf_path).name
        data_path, meta_path = self._get_cache_paths(pdf_filename)
        
        removed = False
        try:
            if data_path.exists():
                data_path.unlink()
                removed = True
            if meta_path.exists():
                meta_path.unlink()
                removed = True
            
            if removed:
                logger.info(f"Invalidated cache for {pdf_filename}")
            return removed
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        json_files = list(self.cache_dir.glob("*.json"))
        
        total_facts = 0
        for jf in json_files:
            try:
                with open(jf, 'r') as f:
                    facts = json.load(f)
                    total_facts += len(facts)
            except:
                pass
        
        return {
            "cached_pdfs": len(json_files),
            "total_cached_facts": total_facts,
            "cache_directory": str(self.cache_dir)
        }
