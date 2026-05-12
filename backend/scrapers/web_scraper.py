# backend/scrapers/web_scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from backend.ingest.chunker import chunk_text
from backend.rag.vectorstore import VectorStore
from backend.config import settings

BASE_URL = "https://www.colgemelli.edu.co"
MAX_PAGES = 50

def _get_links(url: str, visited: set) -> list[str]:
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "MollyBot/1.0"})
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = urljoin(url, a["href"])
            parsed = urlparse(href)
            if parsed.netloc == urlparse(BASE_URL).netloc and href not in visited:
                links.append(href)
        return links
    except Exception:
        return []

def _extract_text(url: str) -> str:
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "MollyBot/1.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)
    except Exception:
        return ""

def _index_chunks(url: str, text: str) -> int:
    chunks = chunk_text(text, doc_id=f"web_{url}", source="web", doc_name=url)
    if chunks:
        vs = VectorStore()
        vs.add_chunks([c["text"] for c in chunks], [c["metadata"] for c in chunks], [c["id"] for c in chunks])
    return len(chunks)

def scrape_website() -> int:
    visited = set()
    to_visit = [BASE_URL]
    total = 0
    while to_visit and len(visited) < MAX_PAGES:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)
        text = _extract_text(url)
        if text:
            total += _index_chunks(url, text)
        to_visit.extend(_get_links(url, visited))
    return total
