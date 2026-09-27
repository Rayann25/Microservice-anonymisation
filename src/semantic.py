import os
from gliner import GLiNER

class SemanticDetector:
    def __init__(self, model_name: str = "urchade/gliner_small-v2.1"):
        """
        Initialisation du détecteur sémantique GLiNER.
        Le modèle small-v2.1 (~150 Mo) est sélectionné pour garantir
        la stabilité mémoire (< 1 Go de RAM) sur Streamlit Community Cloud.
        """
        self.model = GLiNER.from_pretrained(model_name)
        
        # Labels sémantiques ciblés (personnes, organisations, lieux, adresses)
        self.labels = [
            "person",
            "organization",
            "location",
            "address",
            "personne",
            "société",
            "ville"
        ]

    def analyze(self, text: str, threshold: float = 0.4):
        """
        Analyse sémantique zero-shot du texte fourni.
        Retourne une liste d'entités au format attendu par RobustAnonymizationEngine :
        [{"text": "...", "type": "...", "score": 0.95}, ...]
        """
        if not text or not text.strip():
            return []

        try:
            raw_entities = self.model.predict_entities(
                text,
                self.labels,
                threshold=threshold
            )

            entities = []
            for ent in raw_entities:
                entities.append({
                    "text": ent["text"],
                    "type": ent["label"],
                    "score": float(ent.get("score", 1.0))
                })
            return entities

        except Exception as e:
            # Sécurité pour ne pas bloquer le pipeline en cas d'anomalie ponctuelle
            print(f"Avertissement : Erreur lors de l'inférence GLiNER : {e}")
            return []
