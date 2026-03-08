"""
Upload service layer for handling file storage operations with Supabase.
Implements business logic for file uploads, retrievals, and deletions.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from supabase import Client, create_client

from app.config import settings
from app.models.document import Document
from app.models.user import User
from app.schemas.upload_schema import (
    BulkUploadResponse,
    FileDeleteResponse,
    FileListResponse,
    FileUploadResponse,
)
from app.utils.file_handler import FileHandler

from app.workers.ingestion_worker import trigger_ingestion

# Configure logging
logger = logging.getLogger(__name__)


class SupabaseStorageClient:
    """
    Supabase Storage client wrapper.
    Handles low-level storage operations with error handling.
    """
    
    _client: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """
        Get or create Supabase client instance (singleton pattern).
        
        Returns:
            Configured Supabase client
            
        Raises:
            HTTPException: If Supabase credentials are not configured
        """
        if cls._client is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Supabase storage not configured. Please set SUPABASE_URL and SUPABASE_KEY."
                )
            
            try:
                cls._client = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to connect to storage service"
                )
        
        return cls._client
    
    @classmethod
    def upload_file(cls, file_path: str, file_content: bytes, content_type: str) -> dict:
        """
        Upload file to Supabase storage bucket.
        
        Args:
            file_path: Path in the bucket where file will be stored
            file_content: File content as bytes
            content_type: MIME type of the file
            
        Returns:
            Upload response from Supabase
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            client = cls.get_client()
            
            # Upload to Supabase storage
            response = client.storage.from_(settings.SUPABASE_BUCKET_NAME).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "cache-control": "3600",
                    "upsert": "false"  # Prevent overwriting existing files
                }
            )
            
            logger.info(f"File uploaded successfully to {file_path}")
            return response
            
        except Exception as e:
            logger.error(f"Upload failed for {file_path}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to storage: {str(e)}"
            )
    
    @classmethod
    def get_public_url(cls, file_path: str) -> str:
        """
        Get public URL for a file in storage.
        
        Args:
            file_path: Path to file in bucket
            
        Returns:
            Public URL string
        """
        try:
            client = cls.get_client()
            
            # Get public URL
            response = client.storage.from_(settings.SUPABASE_BUCKET_NAME).get_public_url(file_path)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get public URL for {file_path}: {str(e)}")
            return ""
    
    @classmethod
    def delete_file(cls, file_path: str) -> bool:
        """
        Delete file from Supabase storage.
        
        Args:
            file_path: Path to file in bucket
            
        Returns:
            True if deletion successful
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            client = cls.get_client()
            
            # Delete from storage
            client.storage.from_(settings.SUPABASE_BUCKET_NAME).remove([file_path])
            
            logger.info(f"File deleted successfully from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Deletion failed for {file_path}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file from storage: {str(e)}"
            )


class UploadService:
    """
    High-level upload service.
    Orchestrates file validation, storage, and database operations.
    """
    
    def __init__(self, db: Session):
        """
        Initialize upload service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.storage_client = SupabaseStorageClient
    
    async def upload_file(
        self,
        file: UploadFile,
        user: User,
        chatbot_id: UUID,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        is_public: bool = False
    ) -> FileUploadResponse:
        """
        Upload a single file with full validation and storage.
        
        Args:
            file: FastAPI UploadFile object
            user: Authenticated user uploading the file
            chatbot_id: Chatbot to associate file with (required)
            description: Optional file description
            tags: Optional comma-separated tags
            is_public: Whether file should be publicly accessible
            
        Returns:
            FileUploadResponse with upload details
            
        Raises:
            HTTPException: If upload fails at any stage
        """
        try:
            # Process and validate file
            file_data = await FileHandler.process_upload(file, str(user.id))
            
            # Upload to Supabase storage
            self.storage_client.upload_file(
                file_path=file_data["storage_path"],
                file_content=file_data["content"],
                content_type=file_data["content_type"]
            )
            
            # Get public URL if needed
            public_url = None
            if is_public:
                public_url = self.storage_client.get_public_url(file_data["storage_path"])
            
            # Create database record
            document = Document(
                original_filename=file_data["original_filename"],
                unique_filename=file_data["unique_filename"],
                storage_path=file_data["storage_path"],
                file_size=file_data["file_size"],
                file_type=file_data["content_type"],
                file_extension=file_data["extension"],
                public_url=public_url,
                uploaded_by=user.id,
                chatbot_id=chatbot_id,
                description=description,
                tags=tags,
                is_public=is_public,
                processing_status="completed"
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)

            trigger_ingestion(document.id)
            
            logger.info(f"File {file_data['original_filename']} uploaded successfully by user {user.id}")
            
            # Return response
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
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Upload failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}"
            )
    
    async def upload_multiple_files(
        self,
        files: List[UploadFile],
        user: User,
        chatbot_id: UUID,
        is_public: bool = False
    ) -> BulkUploadResponse:
        """
        Upload multiple files in bulk.
        
        Args:
            files: List of FastAPI UploadFile objects
            user: Authenticated user
            chatbot_id: Chatbot to associate files with (required)
            is_public: Whether files should be publicly accessible
            
        Returns:
            BulkUploadResponse with results
        """
        successful_uploads = []
        failed_uploads = []
        
        for file in files:
            try:
                result = await self.upload_file(
                    file=file,
                    user=user,
                    chatbot_id=chatbot_id,
                    is_public=is_public
                )
                successful_uploads.append(result)
            except Exception as e:
                failed_uploads.append({
                    "filename": file.filename or "unknown",
                    "error": str(e)
                })
        
        return BulkUploadResponse(
            total_uploaded=len(successful_uploads),
            total_failed=len(failed_uploads),
            successful_uploads=successful_uploads,
            failed_uploads=failed_uploads
        )
    
    def get_user_files(
        self,
        user: User,
        chatbot_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0
    ) -> FileListResponse:
        """
        Get list of files uploaded by user.
        
        Args:
            user: User to get files for
            chatbot_id: Optional filter by chatbot
            limit: Maximum number of files to return
            offset: Offset for pagination
            
        Returns:
            FileListResponse with file list
        """
        query = self.db.query(Document).filter(
            Document.uploaded_by == user.id,
            Document.is_active == True
        )
        
        if chatbot_id:
            query = query.filter(Document.chatbot_id == chatbot_id)
        
        total = query.count()
        documents = query.order_by(Document.uploaded_at.desc()).limit(limit).offset(offset).all()
        
        files = [
            FileUploadResponse(
                id=str(doc.id),
                filename=doc.original_filename,
                file_path=doc.storage_path,
                file_size=doc.file_size,
                file_type=doc.file_type,
                uploaded_by=str(doc.uploaded_by),
                uploaded_at=doc.uploaded_at,
                public_url=doc.public_url
            )
            for doc in documents
        ]
        
        return FileListResponse(total=total, files=files)
    
    def get_file_by_id(self, file_id: UUID, user: User) -> Document:
        """
        Get file by ID with permission check.
        
        Args:
            file_id: File identifier
            user: User requesting the file
            
        Returns:
            Document instance
            
        Raises:
            HTTPException: If file not found or access denied
        """
        document = self.db.query(Document).filter(
            Document.id == file_id,
            Document.is_active == True
        ).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        # Check permissions (owner or public file)
        if document.uploaded_by != user.id and not document.is_public:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return document
    
    def delete_file(self, file_id: UUID, user: User) -> FileDeleteResponse:
        """
        Delete file from storage and database.
        
        Args:
            file_id: File identifier
            user: User requesting deletion
            
        Returns:
            FileDeleteResponse
            
        Raises:
            HTTPException: If deletion fails or access denied
        """
        # Get document with permission check
        document = self.get_file_by_id(file_id, user)
        
        # Only owner can delete
        if document.uploaded_by != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only file owner can delete"
            )
        
        try:
            # Delete from storage
            self.storage_client.delete_file(document.storage_path)
            
            # Soft delete from database
            document.is_active = False
            from datetime import datetime
            document.deleted_at = datetime.utcnow()
            
            self.db.commit()
            
            logger.info(f"File {file_id} deleted by user {user.id}")
            
            return FileDeleteResponse(
                success=True,
                message="File deleted successfully",
                file_id=str(file_id)
            )
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Delete failed for file {file_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            )


__all__ = ["UploadService", "SupabaseStorageClient"]