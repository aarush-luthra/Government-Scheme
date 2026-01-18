import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional, Dict, List, Union
import logging
import time

# Configure logger
logger = logging.getLogger(__name__)

class IndicBartTranslator:
    """
    Multilingual translator using facebook/nllb-200-distilled-600M
    Optimized for performance:
    1. Dynamic INT8 Quantization (CPU) / Float16 (GPU)
    2. True Batch Inference
    3. Reduced Beam Search
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
        Initialize NLLB translator with hardware optimizations
        """
        self.model_name = model_name
        
        print(f"Loading translation model: {model_name}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self.model.eval()
            
            # Hardware-aware Optimization
            if torch.cuda.is_available():
                self.device = "cuda"
                self.model.to(self.device)
                self.model.half() # Float16 Precision for GPU
                print(f"Model loaded on: GPU (Float16 Mode)")
            else:
                self.device = "cpu"
                # Set quantization engine for CPU
                # Keeps compatibility with Mac (qnnpack) and Linux/Windows (fbgemm)
                engines = torch.backends.quantized.supported_engines
                if "qnnpack" in engines:
                    torch.backends.quantized.engine = "qnnpack"
                elif "fbgemm" in engines:
                    torch.backends.quantized.engine = "fbgemm"
                
                # Dynamic Quantization for CPU (INT8)
                print(f"Quantizing model for CPU (INT8) using engine: {torch.backends.quantized.engine}...")
                self.model = torch.quantization.quantize_dynamic(
                    self.model, {torch.nn.Linear}, dtype=torch.qint8
                )
                print(f"Model loaded on: CPU (Quantized INT8 Mode)")
                
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
        """
        for char in text:
            code = ord(char)
            if 0x0900 <= code <= 0x097F: return "hi_IN"
            elif 0x0980 <= code <= 0x09FF: return "bn_IN"
            elif 0x0A80 <= code <= 0x0AFF: return "gu_IN"
            elif 0x0A00 <= code <= 0x0A7F: return "pa_IN"
            elif 0x0B00 <= code <= 0x0B7F: return "or_IN"
            elif 0x0B80 <= code <= 0x0BFF: return "ta_IN"
            elif 0x0C00 <= code <= 0x0C7F: return "te_IN"
            elif 0x0C80 <= code <= 0x0CFF: return "kn_IN"
            elif 0x0D00 <= code <= 0x0D7F: return "ml_IN"
            elif 0x0600 <= code <= 0x06FF: return "ur_IN"
        return "en_XX"
    
    def translate(
        self, 
        text: str, 
        source_lang: Optional[str] = None,
        target_lang: str = "en_XX",
        max_length: int = 256,
        num_beams: int = 2, # OPTIMIZATION: Reduced from 4 to 2
        temperature: float = 1.0,
        top_p: float = 1.0,
        repetition_penalty: float = 1.2
    ) -> str:
        """
        Translate a single text string
        """
        if not text or not text.strip():
            return ""
            
        # Wrap the single text in a list and use the batch function
        # This reduces code duplication and ensures optimizations apply everywhere
        results = self.batch_translate(
            [text], 
            source_lang=source_lang, 
            target_lang=target_lang,
            batch_size=1,
            num_beams=num_beams
        )
        return results[0] if results else ""

    def batch_translate(
        self, 
        texts: List[str], 
        source_lang: Optional[str] = None,
        target_lang: str = "en_XX",
        batch_size: int = 32, # Increased batch size capability
        num_beams: int = 2
    ) -> List[str]:
        """
        True Batch Translation (Vectorized)
        """
        if not texts:
            return []

        # Auto-detect source language if needed (using first non-empty text)
        if source_lang is None:
            for t in texts:
                if t and t.strip():
                    source_lang = self.detect_language_code(t)
                    break
            if source_lang is None:
                source_lang = "en_XX"
        
        # Map languages
        src_code = self.NLLB_CODES.get(source_lang, "eng_Latn")
        tgt_code = self.NLLB_CODES.get(target_lang, "eng_Latn")
        
        all_translations = []
        
        # Process in chunks to avoid OOM
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Filter empty strings to save compute, but keep track of indices
            # For simplicity in this implementation, we just pass empty strings through 
            # (tokenizer handles them, but inefficiently) or logic gets complex.
            # Efficient Approach: Only send non-empty to model
            
            valid_indices = [j for j, t in enumerate(batch_texts) if t and t.strip()]
            valid_texts = [batch_texts[j] for j in valid_indices]
            
            batch_results = [""] * len(batch_texts)
            
            if valid_texts:
                try:
                    self.tokenizer.src_lang = src_code
                    inputs = self.tokenizer(
                        valid_texts,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512
                    ).to(self.device)
                    
                    forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(tgt_code)
                    
                    with torch.no_grad():
                        outputs = self.model.generate(
                            **inputs,
                            forced_bos_token_id=forced_bos_token_id,
                            max_length=256,
                            num_beams=num_beams, # Reduced beam search
                            early_stopping=True
                        )
                    
                    decoded = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
                    
                    # Fill back into results
                    for idx, trans in zip(valid_indices, decoded):
                        # Repair markdown for each
                        batch_results[idx] = self.repair_markdown(trans.strip())
                        
                except Exception as e:
                    logger.error(f"Batch translation error: {e}")
                    # Fallback or empty strings on error
            
            all_translations.extend(batch_results)
            
        return all_translations

    def repair_markdown(self, text: str) -> str:
        """Fix common markdown errors introduced by translation models."""
        import re
        text = re.sub(r'\*\s+\*', '**', text)
        
        def fix_bold_spaces(match):
            return f"**{match.group(1).strip()}**"
        text = re.sub(r'\*\*\s*(.*?)\s*\*\*', fix_bold_spaces, text)
        
        text = re.sub(r'#\s+#', '##', text)
        
        def insert_newline_before_header(match):
            return f"\n\n{match.group(0)}"
        text = re.sub(r'(?<=\S) (\*\*[^*]+:\*\*)', insert_newline_before_header, text)
        
        text = re.sub(r'(?<=\S) (\d+\.)', r'\n\1', text)
        text = re.sub(r'(\d+)\s+\.', r'\1.', text)
        text = re.sub(r'^\s*-\s*(\S)', r'- \1', text, flags=re.MULTILINE)
        
        return text
    
    def to_english(self, text: str, source_lang: Optional[str] = None) -> str:
        return self.translate(text, source_lang=source_lang, target_lang="en_XX")
    
    def from_english(self, text: str, target_lang: str) -> str:
        return self.translate(text, source_lang="en_XX", target_lang=target_lang)
    
    def indic_to_indic(self, text: str, source_lang: str, target_lang: str) -> str:
        return self.translate(text, source_lang=source_lang, target_lang=target_lang)


if __name__ == "__main__":
    t = IndicBartTranslator()
    
    print("\n--- Testing Single ---")
    res = t.translate("This is a test", target_lang="hi_IN")
    print(f"EN->HI: {res}")
    
    print("\n--- Testing Batch ---")
    batch = ["Hello", "World", "Government Scheme"]
    res_batch = t.batch_translate(batch, target_lang="hi_IN")
    print(f"Batch Results: {res_batch}")