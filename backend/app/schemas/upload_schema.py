"""
Upload-related Pydantic schemas for request validation and response serialization.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class FileUploadResponse(BaseModel):
    """Response schema for successful file upload."""
    
    id: str = Field(..., description="Unique identifier for the uploaded file")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Path to the file in storage")
    file_size: int = Field(..., description="File size in bytes")
    file_type: str = Field(..., description="MIME type of the file")
    uploaded_by: str = Field(..., description="User ID who uploaded the file")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    public_url: Optional[str] = Field(None, description="Public URL if available")

    class Config:
        from_attributes = True


class FileMetadata(BaseModel):
    """Metadata for uploaded file."""
    
    original_filename: str
    file_size: int
    content_type: str
    extension: str


class UploadValidationError(BaseModel):
    """Error response for upload validation failures."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    details: Optional[dict] = Field(None, description="Additional error context")


class FileListResponse(BaseModel):
    """Response schema for listing uploaded files."""
    
    total: int = Field(..., description="Total number of files")
    files: list[FileUploadResponse] = Field(..., description="List of files")


class FileDeleteResponse(BaseModel):
    """Response schema for file deletion."""
    
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Deletion status message")
    file_id: str = Field(..., description="ID of deleted file")


class BulkUploadResponse(BaseModel):
    """Response schema for bulk file upload."""
    
    total_uploaded: int = Field(..., description="Number of successfully uploaded files")
    total_failed: int = Field(..., description="Number of failed uploads")
    successful_uploads: list[FileUploadResponse] = Field(default_factory=list)
    failed_uploads: list[dict] = Field(default_factory=list)
