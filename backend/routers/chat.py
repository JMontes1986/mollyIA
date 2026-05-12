# backend/routers/chat.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User, Conversation, Message
from backend.schemas import ChatRequest, ChatResponse, ConversationOut, MessageOut
from backend.rag.generator import retrieve_and_generate

router = APIRouter(prefix="/chat", tags=["chat"])

def _get_or_create_user(db: Session, clerk_id: str) -> User:
    user = db.query(User).filter_by(clerk_id=clerk_id).first()
    if not user:
        user = User(clerk_id=clerk_id, email="", name="", role="parent")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    user = _get_or_create_user(db, user_data["clerk_id"])
    if req.conversation_id:
        conv = db.query(Conversation).filter_by(id=req.conversation_id, user_id=user.id).first()
        if not conv:
            raise HTTPException(404, "Conversation not found")
    else:
        conv = Conversation(user_id=user.id, title=req.message[:60])
        db.add(conv)
        db.commit()
        db.refresh(conv)
    history = [{"role": m.role, "content": m.content}
               for m in db.query(Message).filter_by(conversation_id=conv.id).order_by(Message.id).all()]
    result = retrieve_and_generate(req.message, history)
    user_msg = Message(conversation_id=conv.id, role="user", content=req.message, sources_json="[]")
    db.add(user_msg)
    db.flush()
    assistant_msg = Message(
        conversation_id=conv.id, role="assistant",
        content=result["answer"], sources_json=json.dumps(result["sources"])
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)
    return ChatResponse(conversation_id=conv.id, message_id=assistant_msg.id,
                        answer=result["answer"], sources=result["sources"])

@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    user = _get_or_create_user(db, user_data["clerk_id"])
    return db.query(Conversation).filter_by(user_id=user.id).order_by(Conversation.updated_at.desc()).all()

@router.get("/conversations/{conv_id}/messages", response_model=list[MessageOut])
async def get_messages(conv_id: int, db: Session = Depends(get_db), user_data: dict = Depends(get_current_user)):
    user = _get_or_create_user(db, user_data["clerk_id"])
    conv = db.query(Conversation).filter_by(id=conv_id, user_id=user.id).first()
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return db.query(Message).filter_by(conversation_id=conv_id).order_by(Message.id).all()
