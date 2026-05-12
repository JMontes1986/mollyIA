# backend/ingest/docx_parser.py
import io
from docx import Document

def extract_text_from_docx_bytes(docx_bytes: bytes) -> str:
    doc = Document(io.BytesIO(docx_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
