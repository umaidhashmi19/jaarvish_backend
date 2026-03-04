"""
Upload API routes.
Defines all file upload-related endpoints with OpenAPI documentation.
"""

from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.controllers.upload_controller import UploadController
from app.db import get_db
from app.models.user import User
from app.schemas.upload_schema import (
    BulkUploadResponse,
    FileDeleteResponse,
    FileListResponse,
    FileUploadResponse,
)
from app.utils.dependencies import get_current_active_user

# Create router with prefix and tags
router = APIRouter(
    prefix="/files",
    tags=["File Upload"],
)


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a single file",
    description="""
    Upload a single file to Supabase storage.
    
    **Supported file types:**
    - Text files (.txt, .md)
    - Documents (.pdf, .docx)
    - Spreadsheets (.csv, .xlsx)
    - Presentations (.pptx)
    
    **Maximum file size:** 50MB (configurable)
    
    Files are validated for:
    - File extension
    - MIME type
    - File size
    - Content integrity
    
    Files are stored in an organized structure:
    `users/{user_id}/{year}/{month}/{unique_filename}`
    """,
    responses={
        201: {"description": "File uploaded successfully"},
        400: {"description": "Invalid file or parameters"},
        413: {"description": "File too large"},
        401: {"description": "Not authenticated"},
        500: {"description": "Server error"},
    }
)
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    chatbot_id: str = Form(..., description="Chatbot ID to associate file with (required)"),
    description: Optional[str] = Form(None, description="Optional file description"),
    tags: Optional[str] = Form(None, description="Optional comma-separated tags"),
    is_public: bool = Form(False, description="Make file publicly accessible"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FileUploadResponse:
    """Upload a single file with optional metadata."""
    return await UploadController.upload_single_file(
        file=file,
        db=db,
        current_user=current_user,
        chatbot_id=chatbot_id,
        description=description,
        tags=tags,
        is_public=is_public
    )


@router.post(
    "/upload/bulk",
    response_model=BulkUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload multiple files",
    description="""
    Upload multiple files in a single request.
    
    Returns detailed results including:
    - Successfully uploaded files
    - Failed uploads with error messages
    - Total counts
    
    Each file is validated independently. Partial success is possible.
    """,
    responses={
        201: {"description": "Files processed (check response for individual results)"},
        400: {"description": "Invalid request"},
        401: {"description": "Not authenticated"},
    }
)
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="List of files to upload"),
    chatbot_id: str = Form(..., description="Chatbot ID to associate files with (required)"),
    is_public: bool = Form(False, description="Make files publicly accessible"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BulkUploadResponse:
    """Upload multiple files at once."""
    return await UploadController.upload_multiple_files(
        files=files,
        db=db,
        current_user=current_user,
        chatbot_id=chatbot_id,
        is_public=is_public
    )


@router.get(
    "/",
    response_model=FileListResponse,
    summary="List uploaded files",
    description="""
    Get a paginated list of files uploaded by the current user.
    
    Supports:
    - Pagination with limit and offset
    - Filtering by chatbot
    - Ordered by upload date (newest first)
    """,
    responses={
        200: {"description": "Files retrieved successfully"},
        400: {"description": "Invalid parameters"},
        401: {"description": "Not authenticated"},
    }
)
def list_files(
    chatbot_id: Optional[str] = Query(None, description="Filter by chatbot ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FileListResponse:
    """List files uploaded by current user."""
    return UploadController.list_user_files(
        db=db,
        current_user=current_user,
        chatbot_id=chatbot_id,
        limit=limit,
        offset=offset
    )


@router.get(
    "/{file_id}",
    response_model=FileUploadResponse,
    summary="Get file details",
    description="""
    Get detailed information about a specific file.
    
    Only the file owner or users with access to public files can view details.
    """,
    responses={
        200: {"description": "File details retrieved"},
        400: {"description": "Invalid file ID"},
        401: {"description": "Not authenticated"},
        403: {"description": "Access denied"},
        404: {"description": "File not found"},
    }
)
def get_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FileUploadResponse:
    """Get details of a specific file."""
    return UploadController.get_file_details(
        file_id=file_id,
        db=db,
        current_user=current_user
    )


@router.delete(
    "/{file_id}",
    response_model=FileDeleteResponse,
    summary="Delete a file",
    description="""
    Delete a file from storage and database.
    
    - Only the file owner can delete files
    - Files are soft-deleted (marked as inactive)
    - Physical file is removed from storage
    """,
    responses={
        200: {"description": "File deleted successfully"},
        400: {"description": "Invalid file ID"},
        401: {"description": "Not authenticated"},
        403: {"description": "Only file owner can delete"},
        404: {"description": "File not found"},
        500: {"description": "Deletion failed"},
    }
)
def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FileDeleteResponse:
    """Delete a file."""
    return UploadController.delete_file(
        file_id=file_id,
        db=db,
        current_user=current_user
    )


@router.get(
    "/health/storage",
    summary="Check storage health",
    description="Verify Supabase storage connectivity",
    tags=["Health"],
    responses={
        200: {"description": "Storage is healthy"},
        500: {"description": "Storage connection failed"},
    }
)
def check_storage_health():
    """Health check for Supabase storage."""
    from app.services.upload_service import SupabaseStorageClient
    
    try:
        # Attempt to get client
        SupabaseStorageClient.get_client()
        return {
            "status": "healthy",
            "service": "Supabase Storage",
            "bucket": "file-upload"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "Supabase Storage",
            "error": str(e)
        }


__all__ = ["router"]