# backend/tests/test_models.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Base, User, Conversation, Message, Document, ScrapeJob

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_user(db):
    user = User(clerk_id="user_abc", email="padre@test.com", name="Juan", role="parent")
    db.add(user)
    db.commit()
    assert db.query(User).filter_by(clerk_id="user_abc").first().name == "Juan"

def test_create_conversation_with_messages(db):
    user = User(clerk_id="u1", email="a@b.com", name="A", role="parent")
    db.add(user)
    db.flush()
    conv = Conversation(user_id=user.id, title="Test conv")
    db.add(conv)
    db.flush()
    msg = Message(conversation_id=conv.id, role="user", content="Hola", sources_json="[]")
    db.add(msg)
    db.commit()
    assert len(db.query(Message).filter_by(conversation_id=conv.id).all()) == 1

def test_document_status_default(db):
    doc = Document(name="test.pdf", category="reglamento", source_type="pdf",
                   r2_key="docs/test.pdf", chunks_count=0, status="processing")
    db.add(doc)
    db.commit()
    assert doc.status == "processing"
