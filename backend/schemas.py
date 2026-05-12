# backend/schemas.py
from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    conversation_id: int | None = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: int
    message_id: int
    answer: str
    sources: list[str]

class ConversationOut(BaseModel):
    id: int
    title: str
    updated_at: datetime
    class Config: from_attributes = True

class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    sources_json: str
    created_at: datetime
    class Config: from_attributes = True

class DocumentOut(BaseModel):
    id: int
    name: str
    category: str
    source_type: str
    chunks_count: int
    status: str
    created_at: datetime
    class Config: from_attributes = True

class ScrapeJobOut(BaseModel):
    id: int
    source: str
    status: str
    chunks_added: int
    error: str
    ran_at: datetime
    class Config: from_attributes = True

class StatsOut(BaseModel):
    docs_indexed: int
    questions_answered: int
    active_users: int
    scrape_jobs: int
