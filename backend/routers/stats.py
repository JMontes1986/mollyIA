# backend/routers/stats.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.auth import require_admin
from backend.models import Document, Message, User, ScrapeJob
from backend.schemas import StatsOut

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("", response_model=StatsOut)
async def get_stats(db: Session = Depends(get_db), _=Depends(require_admin)):
    docs_indexed = db.query(func.count(Document.id)).filter_by(status="indexed").scalar()
    questions_answered = db.query(func.count(Message.id)).filter_by(role="assistant").scalar()
    active_users = db.query(func.count(User.id)).scalar()
    scrape_jobs = db.query(func.count(ScrapeJob.id)).scalar()
    return StatsOut(
        docs_indexed=docs_indexed,
        questions_answered=questions_answered,
        active_users=active_users,
        scrape_jobs=scrape_jobs
    )
