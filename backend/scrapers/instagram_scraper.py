# backend/scrapers/instagram_scraper.py
import instaloader
from backend.ingest.chunker import chunk_text
from backend.rag.vectorstore import VectorStore
from backend.config import settings

def scrape_instagram() -> int:
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, settings.instagram_username)
        captions = []
        for i, post in enumerate(profile.get_posts()):
            if i >= 30:
                break
            if post.caption:
                captions.append(f"[Instagram {post.date.strftime('%Y-%m-%d')}] {post.caption}")
        combined = "\n\n".join(captions)
        if not combined:
            return 0
        chunks = chunk_text(combined, doc_id="instagram_posts", source="instagram", doc_name="Instagram Colegio Gemelli")
        if chunks:
            vs = VectorStore()
            vs.add_chunks([c["text"] for c in chunks], [c["metadata"] for c in chunks], [c["id"] for c in chunks])
        return len(chunks)
    except Exception as e:
        print(f"Instagram scraper error: {e}")
        return 0
