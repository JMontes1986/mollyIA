# backend/scrapers/facebook_scraper.py
import requests
from bs4 import BeautifulSoup
from backend.ingest.chunker import chunk_text
from backend.rag.vectorstore import VectorStore
from backend.config import settings

FB_URL = f"https://www.facebook.com/{settings.facebook_page_id}/posts"

def scrape_facebook() -> int:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "es-CO,es;q=0.9",
    }
    try:
        resp = requests.get(FB_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        posts = []
        for div in soup.find_all("div", {"data-testid": "post_message"}):
            text = div.get_text(separator=" ", strip=True)
            if text:
                posts.append(text)
        if not posts:
            posts = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 40]
        combined = "\n\n".join(posts[:30])
        if not combined:
            return 0
        chunks = chunk_text(combined, doc_id="facebook_posts", source="facebook", doc_name="Facebook Colegio Gemelli")
        if chunks:
            vs = VectorStore()
            vs.add_chunks([c["text"] for c in chunks], [c["metadata"] for c in chunks], [c["id"] for c in chunks])
        return len(chunks)
    except Exception as e:
        print(f"Facebook scraper error: {e}")
        return 0
