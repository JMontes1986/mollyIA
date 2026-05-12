# backend/tests/test_rag.py
import pytest
from unittest.mock import patch, MagicMock
from backend.rag.chunker_helper import split_text
from backend.rag.embedder import Embedder
from backend.rag.vectorstore import VectorStore
from backend.rag.retriever import retrieve_chunks
from backend.rag.generator import build_prompt, SYSTEM_PROMPT

def test_split_text_produces_chunks():
    text = "Hola mundo. " * 200
    chunks = split_text(text)
    assert len(chunks) > 1
    assert all(len(c) > 0 for c in chunks)

def test_embedder_returns_vector():
    embedder = Embedder()
    vec = embedder.embed("Texto de prueba del colegio")
    assert isinstance(vec, list)
    assert len(vec) == 384  # MiniLM-L12-v2 dimension

def test_vectorstore_add_and_query():
    vs = VectorStore(persist_dir="./test_chroma_db")
    vs.add_chunks(
        chunks=["El colegio abre a las 7am", "Las matrículas son en noviembre"],
        metadatas=[{"source": "web"}, {"source": "pdf"}],
        ids=["t1", "t2"]
    )
    results = vs.query("horario de apertura", n_results=1)
    assert len(results) == 1
    assert "7am" in results[0]["text"]
    vs.delete_collection()

def test_build_prompt_includes_context():
    chunks = [{"text": "Matrículas en noviembre", "source": "pdf"}]
    prompt = build_prompt("¿Cuándo son las matrículas?", chunks, history=[])
    assert "noviembre" in prompt
    assert "matrículas" in prompt.lower()

def test_system_prompt_in_spanish():
    assert "Molly" in SYSTEM_PROMPT
    assert "Gemelli" in SYSTEM_PROMPT
    assert "español" in SYSTEM_PROMPT.lower()
