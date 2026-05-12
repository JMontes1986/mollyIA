# backend/routers/scrape.py
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth import require_admin
from backend.models import ScrapeJob
from backend.schemas import ScrapeJobOut

router = APIRouter(prefix="/scrape", tags=["scrape"])

SOURCES = ["web", "facebook", "instagram", "youtube"]

def run_scraper(source: str, db: Session):
    job = ScrapeJob(source=source, status="running")
    db.add(job)
    db.commit()
    db.refresh(job)
    try:
        if source == "web":
            from backend.scrapers.web_scraper import scrape_website
            chunks_added = scrape_website()
        elif source == "facebook":
            from backend.scrapers.facebook_scraper import scrape_facebook
            chunks_added = scrape_facebook()
        elif source == "instagram":
            from backend.scrapers.instagram_scraper import scrape_instagram
            chunks_added = scrape_instagram()
        elif source == "youtube":
            from backend.scrapers.youtube_scraper import scrape_youtube
            chunks_added = scrape_youtube()
        else:
            chunks_added = 0
        job.status = "done"
        job.chunks_added = chunks_added
    except Exception as e:
        job.status = "error"
        job.error = str(e)
    db.commit()

@router.post("/{source}")
async def trigger_scrape(
    source: str, background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), _=Depends(require_admin)
):
    if source not in SOURCES:
        from fastapi import HTTPException
        raise HTTPException(400, f"Source must be one of {SOURCES}")
    background_tasks.add_task(run_scraper, source, db)
    return {"ok": True, "message": f"Scraping {source} started in background"}

@router.get("/jobs", response_model=list[ScrapeJobOut])
async def list_jobs(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(ScrapeJob).order_by(ScrapeJob.ran_at.desc()).limit(20).all()
