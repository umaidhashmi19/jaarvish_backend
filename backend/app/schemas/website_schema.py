"""
Pydantic schemas for website API validation and serialization.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class WebsiteCreate(BaseModel):
    """Schema for creating a new website."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Website name/title")
    url: str = Field(..., description="Website URL")
    chatbot_id: UUID = Field(..., description="ID of the chatbot this website belongs to")
    description: Optional[str] = Field(None, description="Website description")


class WebsiteUpdate(BaseModel):
    """Schema for updating an existing website."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Website name/title")
    url: Optional[str] = Field(None, description="Website URL")
    description: Optional[str] = Field(None, description="Website description")
    is_active: Optional[bool] = Field(None, description="Active status")


class WebsiteResponse(BaseModel):
    """Schema for website response."""
    
    id: UUID
    name: str
    url: str
    chatbot_id: UUID
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WebsiteListResponse(BaseModel):
    """Schema for listing websites."""
    
    websites: list[WebsiteResponse]
    total: int
