import os
import re
import uuid
import pymupdf as fitz
from src.validators import extract_deterministic_pii
from src.semantic import SemanticDetector
from src.vault import SecureVault

# Mots grammaticaux universels du français (mots-outils et auxiliaires uniquement)
FRENCH_GRAMMATICAL_STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "du", "de", "d", "l", "et", "ou",
    "mais", "donc", "or", "ni", "car", "pour", "dans", "par", "sur", "avec",
    "sans", "sous", "vers", "chez", "ce", "cet", "cette", "ces", "mon", "ton",
    "son", "notre", "votre", "leur", "mes", "tes", "ses", "nos", "vos", "leurs",
    "je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles", "me", "te",
    "se", "y", "en", "lui", "être", "avoir", "fait", "faire", "suis", "es", "est",
    "sommes", "êtes", "sont", "ai", "as", "a", "avons", "avez", "ont", "été",
    "ayant", "soit", "au", "aux", "duquel", "auquel", "qui", "que", "quoi", "dont",
    "où", "plus", "moins", "très", "bien", "aussi", "comme", "si"
}

def cluster_occurrences(rects, line_threshold=10):
    if not rects:
        return []
    sorted_rects = sorted(rects, key=lambda r: (r.y0, r.x0))
    occurrences = []
    current_group = [sorted_rects[0]]

    for r in sorted_rects[1:]:
        prev = current_group[-1]
        if 0 < (r.y0 - prev.y0) < line_threshold * 2.5 and abs(r.x0 - prev.x0) < 300:
            current_group.append(r)
        else:
            occurrences.append(current_group)
            current_group = [r]

    occurrences.append(current_group)
    return occurrences

class RobustAnonymizationEngine:
    _detector = None

    def __init__(self):
        if RobustAnonymizationEngine._detector is None:
            RobustAnonymizationEngine._detector = SemanticDetector()
        self.semantic = RobustAnonymizationEngine._detector

    @classmethod
    def process_pdf(cls, input_pdf, output_pdf_path: str = None):
        instance = cls()
        return instance._execute_pdf(input_pdf, output_pdf_path)

    def _execute_pdf(self, input_pdf, output_pdf_path: str = None):
        if isinstance(input_pdf, (bytes, bytearray)):
            doc = fitz.open(stream=input_pdf, filetype="pdf")
            target_path = output_pdf_path or f"anonymized_{uuid.uuid4().hex[:8]}.pdf"
        elif isinstance(input_pdf, str):
            doc = fitz.open(input_pdf)
            target_path = output_pdf_path or f"{os.path.splitext(input_pdf)[0]}_anonymized.pdf"
        else:
            raw_bytes = input_pdf.read() if hasattr(input_pdf, "read") else bytes(input_pdf)
            doc = fitz.open(stream=raw_bytes, filetype="pdf")
            target_path = output_pdf_path or f"anonymized_{uuid.uuid4().hex[:8]}.pdf"

        coref_cache = {}
        mapping_table = {}

        for page in doc:
            text = page.get_text("text")

            deterministic_pii = extract_deterministic_pii(text)
            semantic_pii = self.semantic.analyze(text)
            all_pii = deterministic_pii + semantic_pii

            all_pii = sorted(all_pii, key=lambda x: len(x["text"]), reverse=True)

            filtered_pii = []
            registered_texts = []

            for item in all_pii:
                raw_val = item["text"].strip().strip(" \t\r\n.,;:()[]'\"")
                clean_lower = raw_val.lower()

                if clean_lower in FRENCH_GRAMMATICAL_STOPWORDS or len(clean_lower) < 2:
                    continue

                if any(raw_val.lower() in parent.lower() for parent in registered_texts):
                    continue

                registered_texts.append(raw_val)
                item["text"] = raw_val
                filtered_pii.append(item)

            for item in filtered_pii:
                raw_text = item["text"]
                normalized = raw_text.strip().lower()

                matched_token = None
                for key, assigned in coref_cache.items():
                    if normalized in key or key in normalized:
                        matched_token = assigned
                        break

                if not matched_token:
                    matched_token = f"ID-{uuid.uuid4().hex[:4].upper()}"
                    coref_cache[normalized] = matched_token

                mapping_table[matched_token] = {
                    "original_value": raw_text,
                    "type": item["type"],
                    "score": item.get("score", 1.0)
                }

                rectangles = page.search_for(raw_text)
                if not rectangles and " " in raw_text:
                    rectangles = page.search_for(raw_text.replace(" ", "\u00A0"))

                if not rectangles:
                    continue

                occurrences = cluster_occurrences(rectangles)

                for occ in occurrences:
                    for idx, r in enumerate(occ):
                        box = fitz.Rect(r.x0 - 1.5, r.y0 - 1, r.x1 + 1.5, r.y1 + 1)
                        label = f"[{matched_token}]" if idx == 0 else ""
                        page.add_redact_annot(
                            box,
                            text=label,
                            fontsize=6.5,
                            fill=(0.94, 0.94, 0.96),
                            text_color=(0.12, 0.12, 0.14)
                        )

            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

        doc.save(target_path, garbage=4, deflate=True)
        doc.close()

        session_id = str(uuid.uuid4())
        vault_file = os.path.join(os.path.dirname(target_path) or ".", f"vault_{session_id}.enc")
        sealed_bundle = SecureVault.seal_mapping(mapping_table, output_path=vault_file)

        return {
            "session_id": session_id,
            "output_pdf": target_path,
            "vault_file": vault_file,
            "correspondence_table": mapping_table,
            "encrypted_payload": sealed_bundle
        }

    @classmethod
    def process_raw_text(cls, text: str):
        instance = cls()

        deterministic_pii = extract_deterministic_pii(text)
        semantic_pii = instance.semantic.analyze(text)
        all_pii = deterministic_pii + semantic_pii

        all_pii = sorted(all_pii, key=lambda x: len(x["text"]), reverse=True)

        coref_cache = {}
        mapping_table = {}
        sanitized_text = text
        registered_texts = []

        for item in all_pii:
            raw_val = item["text"].strip().strip(" \t\r\n.,;:()[]'\"")
            clean_lower = raw_val.lower()

            if clean_lower in FRENCH_GRAMMATICAL_STOPWORDS or len(clean_lower) < 2:
                continue

            if any(raw_val.lower() in p.lower() for p in registered_texts):
                continue
            registered_texts.append(raw_val)

            normalized = raw_val.strip().lower()
            matched_token = None
            for key, assigned in coref_cache.items():
                if normalized in key or key in normalized:
                    matched_token = assigned
                    break

            if not matched_token:
                matched_token = f"ID-{uuid.uuid4().hex[:4].upper()}"
                coref_cache[normalized] = matched_token

            mapping_table[matched_token] = {
                "original_value": raw_val,
                "type": item["type"]
            }

            words = [re.escape(w) for w in raw_val.split()]
            if not words:
                continue
            flexible_matcher = r'[\s\u00A0]+'.join(words)

            prefix = r'(?<!\w)' if raw_val[0].isalnum() else ''
            suffix = r'(?!\w)' if raw_val[-1].isalnum() else ''
            pattern = prefix + flexible_matcher + suffix

            sanitized_text = re.sub(pattern, f"[{matched_token}]", sanitized_text)

        encrypted_payload = SecureVault.seal_mapping(mapping_table)

        return {
            "sanitized_text": sanitized_text,
            "encrypted_vault": encrypted_payload,
            "entities_count": len(mapping_table)
        }

    @classmethod
    def rehydrate_text(cls, text_with_tokens: str, encrypted_payload: str) -> str:
        mapping = SecureVault.unseal_mapping(encrypted_payload)
        rehydrated = text_with_tokens
        for token, meta in mapping.items():
            pattern = f"[{token}]"
            if pattern in rehydrated:
                rehydrated = rehydrated.replace(pattern, meta["original_value"])
        return rehydrated

    @classmethod
    def translate_locally(cls, text: str) -> str:
        """Traduction locale hors-ligne via pipeline Hugging Face (sans API cloud tierce)."""
        from transformers import pipeline
        translator = pipeline("translation", model="Helsinki-NLP/opus-mt-fr-en")
        result = translator(text, max_length=512)
        return result[0]["translation_text"]
