# backend/routers/documents.py
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth import require_admin
from backend.models import Document
from backend.schemas import DocumentOut
from backend.ingest.storage import upload_file, delete_file
from backend.ingest.pdf_parser import extract_text_from_pdf_bytes
from backend.ingest.docx_parser import extract_text_from_docx_bytes
from backend.ingest.chunker import chunk_text
from backend.rag.vectorstore import VectorStore

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("", response_model=list[DocumentOut])
async def list_documents(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(Document).order_by(Document.created_at.desc()).all()

@router.post("", response_model=DocumentOut)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("general"),
    db: Session = Depends(get_db),
    _=Depends(require_admin)
):
    file_bytes = await file.read()
    filename = file.filename or "documento"
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in ("pdf", "docx", "txt"):
        raise HTTPException(400, "Solo se aceptan PDF, DOCX o TXT")
    r2_key = f"docs/{uuid.uuid4()}/{filename}"
    upload_file(file_bytes, r2_key, content_type=file.content_type or "application/octet-stream")
    doc = Document(name=filename, category=category, source_type=ext, r2_key=r2_key, status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    if ext == "pdf":
        text = extract_text_from_pdf_bytes(file_bytes)
    elif ext == "docx":
        text = extract_text_from_docx_bytes(file_bytes)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
    chunks = chunk_text(text, doc_id=str(doc.id), source="pdf", doc_name=filename)
    if chunks:
        vs = VectorStore()
        vs.add_chunks(
            chunks=[c["text"] for c in chunks],
            metadatas=[c["metadata"] for c in chunks],
            ids=[c["id"] for c in chunks]
        )
    doc.chunks_count = len(chunks)
    doc.status = "indexed" if chunks else "error"
    db.commit()
    db.refresh(doc)
    return doc

@router.delete("/{doc_id}")
async def delete_document(doc_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    doc = db.query(Document).filter_by(id=doc_id).first()
    if not doc:
        raise HTTPException(404, "Document not found")
    if doc.r2_key:
        try:
            delete_file(doc.r2_key)
        except Exception:
            pass
    VectorStore().delete_by_doc_id(str(doc_id))
    db.delete(doc)
    db.commit()
    return {"ok": True}
