# backend/rag/vectorstore.py
import chromadb
from backend.config import settings

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    return _client

COLLECTION_NAME = "molly_docs"

class VectorStore:
    def __init__(self, persist_dir: str | None = None):
        if persist_dir:
            self._client = chromadb.PersistentClient(path=persist_dir)
        else:
            self._client = _get_client()
        self._col = self._client.get_or_create_collection(
            COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: list[str], metadatas: list[dict], ids: list[str]):
        from backend.rag.embedder import Embedder
        embeddings = Embedder().embed_batch(chunks)
        self._col.add(documents=chunks, embeddings=embeddings, metadatas=metadatas, ids=ids)

    def query(self, text: str, n_results: int = 5) -> list[dict]:
        from backend.rag.embedder import Embedder
        embedding = Embedder().embed(text)
        results = self._col.query(query_embeddings=[embedding], n_results=n_results)
        return [
            {"text": doc, "source": meta.get("source", ""), "doc_name": meta.get("doc_name", "")}
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]

    def delete_by_doc_id(self, doc_id: str):
        results = self._col.get(where={"doc_id": doc_id})
        if results["ids"]:
            self._col.delete(ids=results["ids"])

    def delete_collection(self):
        self._client.delete_collection(COLLECTION_NAME)
