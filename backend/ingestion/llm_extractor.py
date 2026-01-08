"""
LLM Semantic Extractor

Extracts structured facts from PDF page text using an LLM.
Only explicitly stated information is extracted - no summarization or inference.
"""

import json
import logging
from typing import List, Dict, Optional
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
import os

logger = logging.getLogger(__name__)


# JSON Schema for validation
EXTRACTION_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["fact", "category", "confidence"],
        "properties": {
            "fact": {"type": "string", "minLength": 10},
            "category": {
                "type": "string",
                "enum": ["eligibility", "benefit", "document", "process", 
                        "deadline", "contact", "amount", "other"]
            },
            "confidence": {"type": "string", "enum": ["high", "medium"]}
        }
    }
}

EXTRACTION_PROMPT = """You are a document extraction system. Extract ONLY explicitly stated facts from the following government scheme document page.

RULES:
1. Extract only information that is EXPLICITLY written in the text
2. Do NOT summarize or paraphrase - use original wording when possible
3. Do NOT infer or add information not present
4. Do NOT include headers, footers, page numbers, or formatting artifacts
5. Each extracted item must be a single, atomic fact or instruction
6. Skip any content that is just formatting, navigation, or boilerplate

OUTPUT: Return ONLY a valid JSON array where each element has:
- "fact": The extracted information (string, minimum 10 characters)
- "category": One of ["eligibility", "benefit", "document", "process", "deadline", "contact", "amount", "other"]
- "confidence": "high" or "medium" (skip low-confidence extractions)

If no relevant information is found, return an empty array: []

IMPORTANT: Return ONLY the JSON array, no markdown formatting, no explanation.

PAGE TEXT:
{page_content}"""


class LLMExtractor:
    """
    Extracts semantic facts from document text using LLM.
    
    Each fact is validated against a schema and includes
    provenance metadata for traceability.
    """
    
    def __init__(self, model: str = None, temperature: float = 0.0):
        """
        Initialize the LLM extractor.
        
        Args:
            model: OpenAI model to use (default: gpt-4o-mini)
            temperature: LLM temperature (default: 0.0 for deterministic)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        
        self.model = model or os.getenv("LLM_EXTRACTION_MODEL", "gpt-4o-mini")
        self.temperature = temperature
        
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            openai_api_key=api_key
        )
        
        logger.info(f"LLMExtractor initialized with model={self.model}")
    
    def extract_facts(self, page_content: str) -> List[Dict]:
        """
        Extract facts from a single page of text.
        
        Args:
            page_content: Raw text content from a PDF page
            
        Returns:
            List of fact dictionaries with keys: fact, category, confidence
        """
        if not page_content or len(page_content.strip()) < 50:
            logger.debug("Page content too short, skipping extraction")
            return []
        
        prompt = EXTRACTION_PROMPT.format(page_content=page_content)
        
        try:
            response = self.llm.invoke(prompt)
            raw_output = response.content.strip()
            
            # Handle markdown code blocks if present
            if raw_output.startswith("```"):
                lines = raw_output.split("\n")
                raw_output = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
            
            # Parse JSON
            facts = json.loads(raw_output)
            
            # Validate structure
            if not isinstance(facts, list):
                logger.warning("LLM output is not a list, wrapping")
                facts = [facts] if isinstance(facts, dict) else []
            
            # Validate each fact
            validated_facts = []
            for fact in facts:
                if self._validate_fact(fact):
                    validated_facts.append(fact)
                else:
                    logger.debug(f"Invalid fact skipped: {fact}")
            
            logger.info(f"Extracted {len(validated_facts)} valid facts from page")
            return validated_facts
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Raw output: {raw_output[:500]}")
            return []
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return []
    
    def _validate_fact(self, fact: Dict) -> bool:
        """Validate a single fact against the schema."""
        if not isinstance(fact, dict):
            return False
        
        required_keys = {"fact", "category", "confidence"}
        if not required_keys.issubset(fact.keys()):
            return False
        
        if not isinstance(fact["fact"], str) or len(fact["fact"]) < 10:
            return False
        
        valid_categories = {"eligibility", "benefit", "document", "process", 
                          "deadline", "contact", "amount", "other"}
        if fact["category"] not in valid_categories:
            return False
        
        if fact["confidence"] not in {"high", "medium"}:
            return False
        
        return True
    
    def extract_from_documents(
        self, 
        documents: List[Document],
        progress_callback: Optional[callable] = None
    ) -> List[Document]:
        """
        Extract facts from multiple documents (pages).
        
        Args:
            documents: List of LangChain Documents from PDF loader
            progress_callback: Optional callback(current, total) for progress
            
        Returns:
            List of Documents, each containing one extracted fact with metadata
        """
        extracted_docs = []
        total = len(documents)
        
        for i, doc in enumerate(documents):
            if progress_callback:
                progress_callback(i + 1, total)
            
            facts = self.extract_facts(doc.page_content)
            
            for fact in facts:
                # Create new document for each fact
                fact_doc = Document(
                    page_content=fact["fact"],
                    metadata={
                        **doc.metadata,
                        "category": fact["category"],
                        "confidence": fact["confidence"],
                        "extraction_method": "llm",
                        "llm_model": self.model
                    }
                )
                extracted_docs.append(fact_doc)
        
        logger.info(f"Total: Extracted {len(extracted_docs)} facts from {total} pages")
        return extracted_docs
