import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional, Dict, List
import logging

# Configure logger
logger = logging.getLogger(__name__)

class IndicBartTranslator:
    """
    Multilingual translator using facebook/nllb-200-distilled-600M
    Supports major Indic languages + English for translation.
    """
    
    # Internal mapping from our API codes to NLLB codes
    NLLB_CODES = {
        # Indian Languages
        "hi_IN": "hin_Deva",  # Hindi
        "bn_IN": "ben_Beng",  # Bengali
        "gu_IN": "guj_Gujr",  # Gujarati
        "ml_IN": "mal_Mlym",  # Malayalam
        "mr_IN": "mar_Deva",  # Marathi
        "ta_IN": "tam_Taml",  # Tamil
        "te_IN": "tel_Telu",  # Telugu
        "kn_IN": "kan_Knda",  # Kannada
        "pa_IN": "pan_Guru",  # Punjabi
        "or_IN": "ory_Orya",  # Odia
        "as_IN": "asm_Beng",  # Assamese
        "ne_IN": "npi_Deva",  # Nepali
        "ur_IN": "urd_Arab",  # Urdu
        "sa_IN": "san_Deva",  # Sanskrit
        "sd_IN": "snd_Arab",  # Sindhi
        "mai_IN": "mai_Deva", # Maithili
        "doi_IN": "doi_Deva", # Dogri
        "gom_IN": "kok_Deva", # Konkani
        "mni_IN": "mni_Beng", # Manipuri
        "brx_IN": "brx_Deva", # Bodo (using Devanagari script variant if avail or approx)
        "sat_IN": "sat_Olck", # Santali
        "ks_IN": "kas_Arab",  # Kashmiri
        
        # English
        "en_XX": "eng_Latn"   # English
    }

    # Publicly exposed supported languages
    SUPPORTED_LANGUAGES = {
        "hi_IN": "Hindi",
        "bn_IN": "Bengali",
        "gu_IN": "Gujarati",
        "ml_IN": "Malayalam",
        "mr_IN": "Marathi",
        "ta_IN": "Tamil",
        "te_IN": "Telugu",
        "kn_IN": "Kannada",
        "pa_IN": "Punjabi",
        "or_IN": "Odia",
        "as_IN": "Assamese",
        "ne_IN": "Nepali",
        "ur_IN": "Urdu",
        "en_XX": "English"
    }
    
    def __init__(self, model_name: str = "facebook/nllb-200-distilled-600M"):
        """
        Initialize NLLB translator
        
        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        
        print(f"Loading translation model: {model_name}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.eval()
            
            # Check CUDA availability
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            print(f"Model loaded on: {self.device}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise e
    
    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        """Return dictionary of all supported language codes and names"""
        return IndicBartTranslator.SUPPORTED_LANGUAGES.copy()
    
    @staticmethod
    def detect_language_code(text: str) -> Optional[str]:
        """
        Simple heuristic language detection based on Unicode ranges
        Returns language code or None if detection fails
        """
        # Check Unicode ranges for different scripts
        for char in text:
            code = ord(char)
            # Devanagari (Hindi, Marathi, Nepali)
            if 0x0900 <= code <= 0x097F:
                return "hi_IN"
            # Bengali/Assamese
            elif 0x0980 <= code <= 0x09FF:
                return "bn_IN"
            # Gujarati
            elif 0x0A80 <= code <= 0x0AFF:
                return "gu_IN"
            # Gurmukhi (Punjabi)
            elif 0x0A00 <= code <= 0x0A7F:
                return "pa_IN"
            # Oriya
            elif 0x0B00 <= code <= 0x0B7F:
                return "or_IN"
            # Tamil
            elif 0x0B80 <= code <= 0x0BFF:
                return "ta_IN"
            # Telugu
            elif 0x0C00 <= code <= 0x0C7F:
                return "te_IN"
            # Kannada
            elif 0x0C80 <= code <= 0x0CFF:
                return "kn_IN"
            # Malayalam
            elif 0x0D00 <= code <= 0x0D7F:
                return "ml_IN"
            # Arabic script (Urdu, Kashmiri, Sindhi)
            elif 0x0600 <= code <= 0x06FF:
                return "ur_IN"
        
        # Default to English if no Indic script detected
        return "en_XX"
    
    def translate(
        self, 
        text: str, 
        source_lang: Optional[str] = None,
        target_lang: str = "en_XX",
        max_length: int = 256,
        num_beams: int = 4, # Reduced for speed
        temperature: float = 1.0,
        top_p: float = 1.0,
        repetition_penalty: float = 1.2
    ) -> str:
        """
        Translate text from source to target language
        """
        if not text or not text.strip():
            return ""
        
        # Auto-detect source language if not provided
        if source_lang is None:
            source_lang = self.detect_language_code(text)
            if source_lang is None:
                source_lang = "en_XX"
        
        # Map to NLLB codes
        src_code = self.NLLB_CODES.get(source_lang)
        tgt_code = self.NLLB_CODES.get(target_lang)
        
        # Fallback if specific code not found, try to default or error
        if not src_code:
            logger.warning(f"Source language {source_lang} not in NLLB map, using English")
            src_code = "eng_Latn"
        if not tgt_code:
            logger.warning(f"Target language {target_lang} not in NLLB map, using English")
            tgt_code = "eng_Latn"
        
        # Tokenize input
        # NLLB requires setting src_lang in tokenizer
        self.tokenizer.src_lang = src_code
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Get target language token ID
        forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(tgt_code)
        
        # Generate translation
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=forced_bos_token_id,
                max_length=max_length,
                num_beams=num_beams,
                temperature=temperature,
                top_p=top_p,
                repetition_penalty=repetition_penalty,
                early_stopping=True
            )
        
        # Decode output
        translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self.repair_markdown(translation.strip())

    def repair_markdown(self, text: str) -> str:
        """Fix common markdown errors introduced by translation models."""
        import re
        
        # Fix bold formatting: "* * text * *" -> "**text**"
        # Step 1: Fix split asterisks
        text = re.sub(r'\*\s+\*', '**', text)
        
        # Step 2: Fix spaces inside bold tags (e.g. "** text **" -> "**text**")
        # Match ** followed by space, content, space, **
        def fix_bold_spaces(match):
            return f"**{match.group(1).strip()}**"
        
        text = re.sub(r'\*\*\s*(.*?)\s*\*\*', fix_bold_spaces, text)
        
        # Fix headers: "# # Text" -> "## Text"
        text = re.sub(r'#\s+#', '##', text)
        
        # KEY FIX: Force newlines before bold headers if they are stuck to previous text
        # "text **Header:**" -> "text\n\n**Header:**"
        # We look for bold text that acts like a key (e.g., ends with colon or is short)
        def insert_newline_before_header(match):
            return f"\n\n{match.group(0)}"
            
        # Regex: Non-newline chars followed by space, then bold text covering start of new section
        text = re.sub(r'(?<=\S) (\*\*[^*]+:\*\*)', insert_newline_before_header, text)
        
        # Also ensure list items have newlines before them
        text = re.sub(r'(?<=\S) (\d+\.)', r'\n\1', text)
        
        # Fix list items: "1 ." -> "1."
        text = re.sub(r'(\d+)\s+\.', r'\1.', text)
        
        # Fix bullet points if they became "-Text" instead of "- Text" (optional, but good)
        text = re.sub(r'^\s*-\s*(\S)', r'- \1', text, flags=re.MULTILINE)
        
        return text
    
    def to_english(self, text: str, source_lang: Optional[str] = None) -> str:
        return self.translate(text, source_lang=source_lang, target_lang="en_XX")
    
    def from_english(self, text: str, target_lang: str) -> str:
        return self.translate(text, source_lang="en_XX", target_lang=target_lang)
    
    def indic_to_indic(self, text: str, source_lang: str, target_lang: str) -> str:
        return self.translate(text, source_lang=source_lang, target_lang=target_lang)
    
    def batch_translate(
        self, 
        texts: List[str], 
        source_lang: Optional[str] = None,
        target_lang: str = "en_XX",
        batch_size: int = 8
    ) -> List[str]:
        translations = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_translations = [
                self.translate(text, source_lang, target_lang) 
                for text in batch
            ]
            translations.extend(batch_translations)
        return translations


if __name__ == "__main__":
    # Test
    translator = IndicBartTranslator()
    
    # Hindi to English
    text = "यह एक परीक्षण है"
    print(f"HI -> EN: {text} -> {translator.to_english(text)}")
    
    # English to Tamil
    text = "This is a test"
    print(f"EN -> TA: {text} -> {translator.from_english(text, 'ta_IN')}")