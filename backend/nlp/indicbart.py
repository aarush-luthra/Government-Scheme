import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class IndicBartTranslator:
    # ... [Your existing NLLB_CODES and SUPPORTED_LANGUAGES dictionaries remain the same] ...
    
    NLLB_CODES = {
        "hi_IN": "hin_Deva", "bn_IN": "ben_Beng", "gu_IN": "guj_Gujr",
        "ml_IN": "mal_Mlym", "mr_IN": "mar_Deva", "ta_IN": "tam_Taml",
        "te_IN": "tel_Telu", "kn_IN": "kan_Knda", "pa_IN": "pan_Guru",
        "or_IN": "ory_Orya", "as_IN": "asm_Beng", "ne_IN": "npi_Deva",
        "ur_IN": "urd_Arab", "sa_IN": "san_Deva", "sd_IN": "snd_Arab",
        "mai_IN": "mai_Deva", "doi_IN": "doi_Deva", "gom_IN": "kok_Deva",
        "mni_IN": "mni_Beng", "brx_IN": "brx_Deva", "sat_IN": "sat_Olck",
        "ks_IN": "kas_Arab", "en_XX": "eng_Latn"
    }

    SUPPORTED_LANGUAGES = {
        "hi_IN": "Hindi", "bn_IN": "Bengali", "gu_IN": "Gujarati",
        "ml_IN": "Malayalam", "mr_IN": "Marathi", "ta_IN": "Tamil",
        "te_IN": "Telugu", "kn_IN": "Kannada", "pa_IN": "Punjabi",
        "or_IN": "Odia", "as_IN": "Assamese", "ne_IN": "Nepali",
        "ur_IN": "Urdu", "en_XX": "English"
    }

    def __init__(self, model_name: str = "facebook/nllb-200-distilled-600M"):
        print(f"Loading translation model: {model_name}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            self.model.eval()
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            print(f"Model loaded on: {self.device}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise e

    def detect_language_code(self, text: str) -> str:
        """
        Detects Indic scripts. If no Indic script is found, 
        defaults to 'en_XX' (English).
        """
        if not text: return "en_XX"
        
        for char in text:
            code = ord(char)
            if 0x0900 <= code <= 0x097F: return "hi_IN" # Devanagari covers Hindi, Marathi, Nepali
            elif 0x0980 <= code <= 0x09FF: return "bn_IN"
            elif 0x0A80 <= code <= 0x0AFF: return "gu_IN"
            elif 0x0A00 <= code <= 0x0A7F: return "pa_IN"
            elif 0x0B00 <= code <= 0x0B7F: return "or_IN"
            elif 0x0B80 <= code <= 0x0BFF: return "ta_IN"
            elif 0x0C00 <= code <= 0x0C7F: return "te_IN"
            elif 0x0C80 <= code <= 0x0CFF: return "kn_IN"
            elif 0x0D00 <= code <= 0x0D7F: return "ml_IN"
            elif 0x0600 <= code <= 0x06FF: return "ur_IN"
        
        # LOGIC: If source isn't any of the languages above, revert to English
        return "en_XX"

    def batch_translate(self, texts: List[str], source_lang: Optional[str] = None, target_lang: str = "en_XX", batch_size: int = 8) -> List[str]:
        """
        Optimized Batch Translation (Processes multiple texts at once)
        """
        # 1. Resolve Source/Target Codes
        # If source is not provided, detect from the first text in batch (or default to en_XX)
        if not source_lang:
            source_lang = self.detect_language_code(texts[0] if texts else "")
        
        src_code = self.NLLB_CODES.get(source_lang, "eng_Latn")
        tgt_code = self.NLLB_CODES.get(target_lang, "eng_Latn")
        
        self.tokenizer.src_lang = src_code
        translations = []

        # 2. Process in Batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            
            # Tokenize ALL texts in the batch at once
            inputs = self.tokenizer(
                batch_texts, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            ).to(self.device)

            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(tgt_code)

            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=forced_bos_token_id,
                    max_length=256
                )

            # Decode ALL outputs at once
            batch_decoded = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
            translations.extend([t.strip() for t in batch_decoded])

        return translations

    def get_supported_languages(self) -> Dict[str, str]:
        return self.SUPPORTED_LANGUAGES

    def translate(self, text: str, source_lang: Optional[str] = None, target_lang: str = "en_XX") -> str:
        """
        Translate a single text string.
        """
        if not text:
            return ""
        
        # Use batch_translate for single item
        translations = self.batch_translate([text], source_lang=source_lang, target_lang=target_lang)
        return translations[0] if translations else ""

    def to_english(self, text: str, source_lang: Optional[str] = None) -> str:
        """
        Translate text to English.
        """
        return self.translate(text, source_lang=source_lang, target_lang="en_XX")

    def from_english(self, text: str, target_lang: str) -> str:
        """
        Translate text from English to target language.
        """
        return self.translate(text, source_lang="en_XX", target_lang=target_lang)


if __name__ == "__main__":
    # Test
    translator = IndicBartTranslator()
    
    # Hindi to English
    text = "यह एक परीक्षण है"
    print(f"HI -> EN: {text} -> {translator.to_english(text)}")
    
    # English to Tamil
    text = "This is a test"
    print(f"EN -> TA: {text} -> {translator.from_english(text, 'ta_IN')}")