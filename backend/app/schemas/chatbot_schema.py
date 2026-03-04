"""
Pydantic schemas for chatbot API validation and serialization.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChatbotCreate(BaseModel):
    """Schema for creating a new chatbot."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Chatbot name")
    description: Optional[str] = Field(None, description="Chatbot description")


class ChatbotUpdate(BaseModel):
    """Schema for updating an existing chatbot."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Chatbot name")
    description: Optional[str] = Field(None, description="Chatbot description")
    is_active: Optional[bool] = Field(None, description="Active status")


class ChatbotResponse(BaseModel):
    """Schema for chatbot response."""
    
    id: UUID
    name: str
    description: Optional[str]
    owner_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatbotListResponse(BaseModel):
    """Schema for listing chatbots."""
    
    chatbots: list[ChatbotResponse]
    total: int
