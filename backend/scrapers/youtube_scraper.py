# backend/scrapers/youtube_scraper.py
from googleapiclient.discovery import build
from backend.ingest.chunker import chunk_text
from backend.rag.vectorstore import VectorStore
from backend.config import settings

CHANNEL_QUERY = "Colegio Gemelli"

def _get_youtube_service():
    return build("youtube", "v3", developerKey=settings.youtube_api_key)

def _index_chunks(text: str, source_name: str) -> int:
    chunks = chunk_text(text, doc_id="youtube_videos", source="youtube", doc_name=source_name)
    if chunks:
        vs = VectorStore()
        vs.add_chunks([c["text"] for c in chunks], [c["metadata"] for c in chunks], [c["id"] for c in chunks])
    return len(chunks)

def scrape_youtube() -> int:
    youtube = _get_youtube_service()
    request = youtube.search().list(q=CHANNEL_QUERY, part="snippet", type="video", maxResults=25)
    response = request.execute()
    entries = []
    for item in response.get("items", []):
        snippet = item["snippet"]
        entries.append(f"[YouTube] {snippet['title']}\n{snippet['description']}")
    combined = "\n\n".join(entries)
    if not combined:
        return 0
    return _index_chunks(combined, "YouTube Colegio Gemelli")
