import re
import threading
import torch

class SemanticDetector:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SemanticDetector, cls).__new__(cls)
                cls._instance._init_detector()
            return cls._instance

    def _init_detector(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.backend = None
        self.is_loading = True

        threading.Thread(target=self._load_model, daemon=True).start()

    def _load_model(self):
        try:
            from gliner import GLiNER
            self.model = GLiNER.from_pretrained("urchade/gliner_multi-v2.1")
            self.model.to(self.device)
            self.backend = "gliner"
            self.is_loading = False
            return
        except Exception:
            pass

        try:
            from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
            model_id = "Jean-Baptiste/camembert-ner"
            tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
            model = AutoModelForTokenClassification.from_pretrained(model_id)
            self.model = pipeline(
                "token-classification",
                model=model,
                tokenizer=tokenizer,
                aggregation_strategy="simple",
                device=0 if self.device == "cuda" else -1
            )
            self.backend = "transformers"
        except Exception:
            self.model = None
            self.backend = None
        finally:
            self.is_loading = False

    def analyze(self, text: str):
        if not text or not text.strip() or self.is_loading or not self.model:
            return []

        results = []

        if self.backend == "gliner":
            labels = ["personne", "nom de famille", "entreprise", "organisation", "ville", "lieu"]
            try:
                entities = self.model.predict_entities(text, labels, threshold=0.38)
                for ent in entities:
                    label = ent["label"]
                    norm_type = "PER" if label in ["personne", "nom de famille"] else (
                        "ORG" if label in ["entreprise", "organisation"] else "LOC"
                    )
                    results.append({
                        "type": norm_type,
                        "text": ent["text"].strip(),
                        "start": ent["start"],
                        "end": ent["end"],
                        "score": float(ent["score"])
                    })
            except Exception:
                pass

        elif self.backend == "transformers":
            try:
                preds = self.model(text[:3000])
                for p in preds:
                    word = p["word"].strip()
                    word = re.sub(r'^[#\-_\s]+', '', word)
                    if len(word) > 1 and p["score"] > 0.60:
                        results.append({
                            "type": p["entity_group"],
                            "text": word,
                            "start": p["start"],
                            "end": p["end"],
                            "score": float(p["score"])
                        })
            except Exception:
                pass

        return results
