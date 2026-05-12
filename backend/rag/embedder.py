# backend/rag/embedder.py
from sentence_transformers import SentenceTransformer

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model

class Embedder:
    def embed(self, text: str) -> list[float]:
        return _get_model().encode(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return _get_model().encode(texts).tolist()
