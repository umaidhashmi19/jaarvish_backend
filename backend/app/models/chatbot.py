"""
Chatbot model for organizing documents and user work.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Chatbot(Base):
    """
    SQLAlchemy model for chatbots.
    One user can have many chatbots.
    One chatbot can contain multiple documents.
    """
    
    __tablename__ = "chatbots"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Owner
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Relationships
    documents = relationship("Document", back_populates="chatbot", lazy="dynamic")
    websites = relationship("Website", back_populates="chatbot", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Chatbot(id={self.id}, name={self.name})>"
