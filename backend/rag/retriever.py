# backend/rag/retriever.py
from backend.rag.vectorstore import VectorStore

def retrieve_chunks(question: str, n_results: int = 5) -> list[dict]:
    vs = VectorStore()
    return vs.query(question, n_results=n_results)
