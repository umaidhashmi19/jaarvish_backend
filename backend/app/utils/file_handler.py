"""
File handling utilities for upload validation and processing.
Provides secure file validation, type checking, and metadata extraction.
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import filetype
from fastapi import HTTPException, UploadFile, status

from app.config import settings


class FileValidator:
    """
    Validates uploaded files against security and business rules.
    Implements defense-in-depth validation strategy.
    """

    @staticmethod
    def validate_file_size(file_size: int) -> None:
        """
        Validate file size against configured maximum.
        
        Args:
            file_size: Size of the file in bytes
            
        Raises:
            HTTPException: If file exceeds maximum allowed size
        """
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
            )

    @staticmethod
    def validate_file_extension(filename: str) -> str:
        """
        Validate and extract file extension.
        
        Args:
            filename: Original filename
            
        Returns:
            Normalized file extension (lowercase with dot)
            
        Raises:
            HTTPException: If extension is not allowed
        """
        file_extension = Path(filename).suffix.lower()
        
        if not file_extension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have an extension"
            )
        
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            allowed = ", ".join(settings.ALLOWED_EXTENSIONS)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file_extension}' not allowed. Allowed types: {allowed}"
            )
        
        return file_extension

    @staticmethod
    async def validate_file_content(file: UploadFile) -> Tuple[bytes, str]:
        """
        Validate file content and detect actual MIME type.
        Prevents MIME type spoofing attacks.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (file_content, detected_mime_type)
            
        Raises:
            HTTPException: If content validation fails
        """
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer for potential re-reading
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        # Detect actual file type from content (magic bytes)
        kind = filetype.guess(content)
        
        # For text-based files (txt, md, csv), filetype may return None
        # These are validated by extension only
        text_extensions = {".txt", ".md", ".csv"}
        file_ext = Path(file.filename or "").suffix.lower()
        
        if kind is None and file_ext in text_extensions:
            # Validate it's actually text by attempting to decode
            try:
                content.decode('utf-8')
                detected_mime = "text/plain" if file_ext == ".txt" else \
                               "text/markdown" if file_ext == ".md" else \
                               "text/csv"
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File appears to be binary, not a valid {file_ext} text file"
                )
        elif kind is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to determine file type"
            )
        else:
            detected_mime = kind.mime
            
            # Verify detected MIME type is allowed
            if detected_mime not in settings.ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File content type '{detected_mime}' does not match allowed types"
                )
        
        return content, detected_mime

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove any null bytes
        filename = filename.replace('\0', '')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename

    @staticmethod
    def generate_unique_filename(original_filename: str, user_id: str) -> str:
        """
        Generate a unique filename to prevent collisions.
        
        Args:
            original_filename: Original uploaded filename
            user_id: ID of the user uploading the file
            
        Returns:
            Unique filename with timestamp and UUID
        """
        sanitized = FileValidator.sanitize_filename(original_filename)
        name, ext = os.path.splitext(sanitized)
        
        # Create unique filename: timestamp_uuid_originalname.ext
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        unique_name = f"{timestamp}_{unique_id}_{name}{ext}"
        
        return unique_name

    @staticmethod
    def generate_storage_path(user_id: str, filename: str) -> str:
        """
        Generate organized storage path structure.
        
        Args:
            user_id: ID of the user uploading the file
            filename: Filename to store
            
        Returns:
            Storage path in format: users/{user_id}/{year}/{month}/{filename}
        """
        now = datetime.utcnow()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        
        # Organize by user and date for better management
        storage_path = f"users/{user_id}/{year}/{month}/{filename}"
        
        return storage_path


class FileHandler:
    """
    High-level file handling operations.
    Orchestrates validation and processing workflows.
    """
    
    @staticmethod
    async def process_upload(
        file: UploadFile,
        user_id: str
    ) -> dict:
        """
        Process and validate an uploaded file.
        
        Args:
            file: FastAPI UploadFile object
            user_id: ID of the user uploading the file
            
        Returns:
            Dictionary containing file metadata and content
            
        Raises:
            HTTPException: If validation fails
        """
        validator = FileValidator()
        
        # Validate filename
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        # Validate extension
        extension = validator.validate_file_extension(file.filename)
        
        # Validate content and get actual MIME type
        content, detected_mime = await validator.validate_file_content(file)
        
        # Validate file size
        file_size = len(content)
        validator.validate_file_size(file_size)
        
        # Generate unique filename and storage path
        unique_filename = validator.generate_unique_filename(file.filename, user_id)
        storage_path = validator.generate_storage_path(user_id, unique_filename)
        
        return {
            "content": content,
            "original_filename": file.filename,
            "unique_filename": unique_filename,
            "storage_path": storage_path,
            "file_size": file_size,
            "content_type": detected_mime,
            "extension": extension,
        }


__all__ = [
    "FileValidator",
    "FileHandler",
]