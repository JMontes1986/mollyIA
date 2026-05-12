# backend/tests/test_scrapers.py
from unittest.mock import patch, MagicMock

def test_web_scraper_returns_int(mocker):
    mocker.patch("requests.get", return_value=MagicMock(
        status_code=200,
        text="<html><body><p>El colegio Gemelli abre en enero</p></body></html>",
        content=b"<html><body><p>El colegio Gemelli abre en enero</p></body></html>"
    ))
    mocker.patch("backend.scrapers.web_scraper._index_chunks", return_value=3)
    from backend.scrapers.web_scraper import scrape_website
    result = scrape_website()
    assert isinstance(result, int)

def test_youtube_scraper_returns_int(mocker):
    mock_service = MagicMock()
    mock_service.search().list().execute.return_value = {
        "items": [{"id": {"videoId": "abc123"}, "snippet": {
            "title": "Video del colegio", "description": "Evento de grado 2025"
        }}]
    }
    mocker.patch("backend.scrapers.youtube_scraper._get_youtube_service", return_value=mock_service)
    mocker.patch("backend.scrapers.youtube_scraper._index_chunks", return_value=2)
    from backend.scrapers.youtube_scraper import scrape_youtube
    result = scrape_youtube()
    assert isinstance(result, int)
