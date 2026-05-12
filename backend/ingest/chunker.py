# backend/ingest/chunker.py
import hashlib
from backend.rag.chunker_helper import split_text

def chunk_text(text: str, doc_id: str, source: str, doc_name: str) -> list[dict]:
    if not text.strip():
        return []
    raw_chunks = split_text(text)
    result = []
    for i, chunk in enumerate(raw_chunks):
        chunk_id = hashlib.md5(f"{doc_id}_{i}_{chunk[:32]}".encode()).hexdigest()
        result.append({
            "id": chunk_id,
            "text": chunk,
            "metadata": {"doc_id": doc_id, "source": source, "doc_name": doc_name, "chunk_index": i}
        })
    return result
