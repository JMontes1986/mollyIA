# backend/rag/chunker_helper.py
from langchain_text_splitters import RecursiveCharacterTextSplitter

_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

def split_text(text: str) -> list[str]:
    return [c.page_content for c in _splitter.create_documents([text])]
