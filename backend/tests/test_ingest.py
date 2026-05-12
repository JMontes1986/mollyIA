# backend/tests/test_ingest.py
import pytest
import io
from unittest.mock import patch, MagicMock
from backend.ingest.chunker import chunk_text
from backend.ingest.pdf_parser import extract_text_from_pdf_bytes
from backend.ingest.docx_parser import extract_text_from_docx_bytes

def test_chunk_text_returns_list():
    long_text = "El colegio Gemelli fue fundado. " * 100
    chunks = chunk_text(long_text, doc_id="d1", source="pdf", doc_name="test.pdf")
    assert len(chunks) > 1
    assert all("text" in c and "metadata" in c and "id" in c for c in chunks)
    assert chunks[0]["metadata"]["doc_id"] == "d1"
    assert chunks[0]["metadata"]["source"] == "pdf"

def test_chunk_text_empty_returns_empty():
    assert chunk_text("", doc_id="d1", source="pdf", doc_name="test.pdf") == []

def test_extract_pdf_bytes():
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hola desde el colegio Gemelli")
    pdf_bytes = doc.tobytes()
    text = extract_text_from_pdf_bytes(pdf_bytes)
    assert "Gemelli" in text

def test_extract_docx_bytes():
    from docx import Document
    doc = Document()
    doc.add_paragraph("Reglamento del Colegio Gemelli 2026")
    buf = io.BytesIO()
    doc.save(buf)
    text = extract_text_from_docx_bytes(buf.getvalue())
    assert "Gemelli" in text
