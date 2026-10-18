import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="user")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), default="New Support Conversation")
    status = Column(String(32), default="active")  # active, closed, escalated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")
    tickets = relationship("Ticket", back_populates="session")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    sender = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    sentiment = Column(String(30), nullable=True)  # positive, neutral, frustrated, angry
    sentiment_score = Column(Float, nullable=True)  # 0.0 to 1.0 (1.0 = highly positive, 0.0 = highly frustrated)
    intent = Column(String(50), nullable=True)  # rag_query, general_inquiry, complaint, billing, greeting
    agent_trajectory = Column(JSON, nullable=True)  # List of agents involved in processing
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")
    feedbacks = relationship("Feedback", back_populates="message")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_number = Column(String(32), unique=True, index=True, nullable=False)
    session_id = Column(String(64), ForeignKey("chat_sessions.session_id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    customer_name = Column(String(255), default="Anonymous Customer")
    customer_email = Column(String(255), nullable=True)
    issue_summary = Column(String(500), nullable=False)
    details = Column(Text, nullable=True)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    status = Column(String(30), default="escalated")  # open, escalated, in_progress, resolved, closed
    sentiment_score = Column(Float, nullable=True)
    agent_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    session = relationship("ChatSession", back_populates="tickets")
    user = relationship("User", back_populates="tickets")


class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="General")  # Return Policy, Shipping, Billing, Technical
    content = Column(Text, nullable=False)
    metadata_info = Column(JSON, nullable=True)
    embedding_id = Column(String(64), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(36), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(64), nullable=False)
    rating = Column(Integer, nullable=False)  # 1 (negative) or 5 (positive)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("ChatMessage", back_populates="feedbacks")
