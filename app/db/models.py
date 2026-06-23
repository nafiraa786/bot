from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.db.base import Base
import enum

class ApprovalStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    relationship_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_blocked = Column(Boolean, default=False)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chat_id = Column(Integer, index=True)
    type = Column(String)  # private, group
    last_message_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    summary = Column(Text, nullable=True)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    sender_type = Column(String)  # user, bot
    content = Column(Text)
    msg_type = Column(String, default="text")  # text, voice, image
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_approved = Column(Boolean, default=True)

class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    embedding = Column(Vector(1536))  # For OpenAI embeddings
    category = Column(String)  # factual, emotional, preference
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ApprovalQueue(Base):
    __tablename__ = "approval_queue"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    content = Column(Text)
    reason = Column(String)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PersonaSettings(Base):
    __tablename__ = "persona_settings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Default")
    tone = Column(String)
    style = Column(String)
    humor_level = Column(Float, default=0.5)
    formality = Column(Float, default=0.5)
    response_length = Column(String, default="medium")
    system_prompt = Column(Text)
    is_active = Column(Boolean, default=True)

class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
