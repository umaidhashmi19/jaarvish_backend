"""
Website model for tracking website URLs associated with chatbots.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Website(Base):
    """
    SQLAlchemy model for websites.
    One chatbot can have many websites.
    """
    
    __tablename__ = "websites"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Unique website identifier"
    )

    # Website information
    name = Column(
        String(255),
        nullable=False,
        comment="Website name/title"
    )
    
    url = Column(
        Text,
        nullable=False,
        comment="Website URL"
    )
    
    # Ownership and relationships
    chatbot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chatbots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Associated chatbot"
    )
    
    # Metadata
    description = Column(
        Text,
        nullable=True,
        comment="Optional website description"
    )
    
    # Status flags
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether the website is active (soft delete support)"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Creation timestamp"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )

    # Relationships
    chatbot = relationship(
        "Chatbot",
        back_populates="websites",
        foreign_keys=[chatbot_id]
    )

    def __repr__(self) -> str:
        return (
            f"<Website(id={self.id}, "
            f"name={self.name}, "
            f"chatbot_id={self.chatbot_id})>"
        )

    def to_dict(self) -> dict:
        """Convert website instance to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "url": self.url,
            "chatbot_id": str(self.chatbot_id),
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
