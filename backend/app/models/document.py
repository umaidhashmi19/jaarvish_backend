"""
Document model for tracking uploaded files in the database.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


class Document(Base):
    """
    SQLAlchemy model for uploaded documents/files.
    Tracks file metadata and storage information.
    """
    
    __tablename__ = "documents"

    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Unique document identifier"
    )

    # File information
    original_filename = Column(
        String(255),
        nullable=False,
        comment="Original filename as uploaded by user"
    )
    
    unique_filename = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique filename in storage system"
    )
    
    storage_path = Column(
        String(512),
        nullable=False,
        unique=True,
        index=True,
        comment="Full path to file in storage bucket"
    )
    
    file_size = Column(
        Integer,
        nullable=False,
        comment="File size in bytes"
    )
    
    file_type = Column(
        String(100),
        nullable=False,
        comment="MIME type of the file"
    )
    
    file_extension = Column(
        String(20),
        nullable=False,
        index=True,
        comment="File extension (e.g., .pdf, .docx)"
    )
    
    # Storage URLs
    public_url = Column(
        Text,
        nullable=True,
        comment="Public URL if file is publicly accessible"
    )
    
    # Ownership and relationships
    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who uploaded the file"
    )
    
    # Optional: link to chatbot if needed
    chatbot_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chatbots.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Associated chatbot (optional)"
    )
    
    # Metadata
    description = Column(
        Text,
        nullable=True,
        comment="Optional file description"
    )
    
    tags = Column(
        Text,
        nullable=True,
        comment="Comma-separated tags for categorization"
    )
    
    # Status flags
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether the file is active (soft delete support)"
    )
    
    is_public = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the file is publicly accessible"
    )
    
    # Processing status (for future features like virus scanning, indexing)
    processing_status = Column(
        String(50),
        default="completed",
        nullable=False,
        comment="Processing status: pending, processing, completed, failed"
    )
    
    # Timestamps
    uploaded_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="Upload timestamp"
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )
    
    deleted_at = Column(
        DateTime,
        nullable=True,
        comment="Soft delete timestamp"
    )

    # Relationships
    uploader = relationship(
        "User",
        back_populates="documents",
        foreign_keys=[uploaded_by]
    )
    
    chatbot = relationship(
        "Chatbot",
        back_populates="documents",
        foreign_keys=[chatbot_id]
    )

    def __repr__(self) -> str:
        return (
            f"<Document(id={self.id}, "
            f"filename={self.original_filename}, "
            f"uploaded_by={self.uploaded_by})>"
        )

    def to_dict(self) -> dict:
        """Convert document instance to dictionary."""
        return {
            "id": str(self.id),
            "original_filename": self.original_filename,
            "unique_filename": self.unique_filename,
            "storage_path": self.storage_path,
            "file_size": self.file_size,
            "file_type": self.file_type,
            "file_extension": self.file_extension,
            "public_url": self.public_url,
            "uploaded_by": str(self.uploaded_by),
            "chatbot_id": str(self.chatbot_id) if self.chatbot_id else None,
            "description": self.description,
            "tags": self.tags.split(",") if self.tags else [],
            "is_active": self.is_active,
            "is_public": self.is_public,
            "processing_status": self.processing_status,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }