"""
Upload controller layer.
Handles HTTP request/response logic and delegates business logic to service layer.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.upload_schema import (
    BulkUploadResponse,
    FileDeleteResponse,
    FileListResponse,
    FileUploadResponse,
)
from app.services.upload_service import UploadService


class UploadController:
    """
    Controller for file upload operations.
    Serves as the interface between routes and service layer.
    """
    
    @staticmethod
    async def upload_single_file(
        file: UploadFile,
        db: Session,
        current_user: User,
        chatbot_id: str,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        is_public: bool = False
    ) -> FileUploadResponse:
        """
        Handle single file upload request.
        
        Args:
            file: Uploaded file
            db: Database session
            current_user: Authenticated user
            chatbot_id: Chatbot ID (required)
            description: Optional file description
            tags: Optional tags
            is_public: Whether file is public
            
        Returns:
            FileUploadResponse
        """
        # Convert chatbot_id string to UUID
        try:
            chatbot_uuid = UUID(chatbot_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chatbot ID format"
            )
        
        # Delegate to service
        service = UploadService(db)
        return await service.upload_file(
            file=file,
            user=current_user,
            chatbot_id=chatbot_uuid,
            description=description,
            tags=tags,
            is_public=is_public
        )
    
    @staticmethod
    async def upload_multiple_files(
        files: List[UploadFile],
        db: Session,
        current_user: User,
        chatbot_id: str,
        is_public: bool = False
    ) -> BulkUploadResponse:
        """
        Handle multiple file upload request.
        
        Args:
            files: List of uploaded files
            db: Database session
            current_user: Authenticated user
            chatbot_id: Chatbot ID (required)
            is_public: Whether files are public
            
        Returns:
            BulkUploadResponse
        """
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )
        
        # Convert chatbot_id string to UUID
        try:
            chatbot_uuid = UUID(chatbot_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid chatbot ID format"
            )
        
        # Delegate to service
        service = UploadService(db)
        return await service.upload_multiple_files(
            files=files,
            user=current_user,
            chatbot_id=chatbot_uuid,
            is_public=is_public
        )
    
    @staticmethod
    def list_user_files(
        db: Session,
        current_user: User,
        chatbot_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> FileListResponse:
        """
        List files uploaded by current user.
        
        Args:
            db: Database session
            current_user: Authenticated user
            chatbot_id: Optional chatbot filter
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            FileListResponse
        """
        # Validate pagination parameters
        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 1000"
            )
        
        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative"
            )
        
        # Convert chatbot_id string to UUID if provided
        chatbot_uuid = None
        if chatbot_id:
            try:
                chatbot_uuid = UUID(chatbot_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid chatbot ID format"
                )
        
        # Delegate to service
        service = UploadService(db)
        return service.get_user_files(
            user=current_user,
            chatbot_id=chatbot_uuid,
            limit=limit,
            offset=offset
        )
    
    @staticmethod
    def get_file_details(
        file_id: str,
        db: Session,
        current_user: User
    ) -> FileUploadResponse:
        """
        Get details of a specific file.
        
        Args:
            file_id: File identifier
            db: Database session
            current_user: Authenticated user
            
        Returns:
            FileUploadResponse
        """
        # Convert file_id string to UUID
        try:
            file_uuid = UUID(file_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file ID format"
            )
        
        # Delegate to service
        service = UploadService(db)
        document = service.get_file_by_id(file_uuid, current_user)
        
        return FileUploadResponse(
            id=str(document.id),
            filename=document.original_filename,
            file_path=document.storage_path,
            file_size=document.file_size,
            file_type=document.file_type,
            uploaded_by=str(document.uploaded_by),
            uploaded_at=document.uploaded_at,
            public_url=document.public_url
        )
    
    @staticmethod
    def delete_file(
        file_id: str,
        db: Session,
        current_user: User
    ) -> FileDeleteResponse:
        """
        Delete a file.
        
        Args:
            file_id: File identifier
            db: Database session
            current_user: Authenticated user
            
        Returns:
            FileDeleteResponse
        """
        # Convert file_id string to UUID
        try:
            file_uuid = UUID(file_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file ID format"
            )
        
        # Delegate to service
        service = UploadService(db)
        return service.delete_file(file_uuid, current_user)


__all__ = ["UploadController"]