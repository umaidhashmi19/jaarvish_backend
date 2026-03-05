"""
API routes for website management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.controllers.website_controller import WebsiteController
from app.models.user import User
from app.schemas.website_schema import (
    WebsiteCreate,
    WebsiteListResponse,
    WebsiteResponse,
    WebsiteUpdate,
)
from app.utils.dependencies import get_current_user, get_db

router = APIRouter(
    prefix="/websites",
    tags=["Websites"]
)


@router.post(
    "",
    response_model=WebsiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new website"
)
def create_website(
    website_data: WebsiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WebsiteResponse:
    """
    Create a new website for a chatbot.
    
    - **name**: Name/title of the website (required)
    - **url**: Website URL (required)
    - **chatbot_id**: ID of the chatbot this website belongs to (required)
    - **description**: Optional description of the website
    """
    return WebsiteController.create_website(
        db=db,
        website_data=website_data,
        current_user=current_user
    )


@router.get(
    "",
    response_model=WebsiteListResponse,
    summary="List all websites"
)
def list_all_websites(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WebsiteListResponse:
    """
    Get all websites across all chatbots for the authenticated user.
    
    Supports pagination with skip and limit parameters.
    """
    return WebsiteController.list_all_websites(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit
    )


@router.get(
    "/chatbot/{chatbot_id}",
    response_model=WebsiteListResponse,
    summary="List websites for a specific chatbot"
)
def list_websites_by_chatbot(
    chatbot_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WebsiteListResponse:
    """
    Get all websites for a specific chatbot.
    
    Supports pagination with skip and limit parameters.
    """
    return WebsiteController.list_websites_by_chatbot(
        db=db,
        chatbot_id=chatbot_id,
        current_user=current_user,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{website_id}",
    response_model=WebsiteResponse,
    summary="Get a website by ID"
)
def get_website(
    website_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WebsiteResponse:
    """
    Get a specific website by ID.
    
    Returns 404 if the website doesn't exist or doesn't belong to the user's chatbot.
    """
    return WebsiteController.get_website(
        db=db,
        website_id=website_id,
        current_user=current_user
    )


@router.put(
    "/{website_id}",
    response_model=WebsiteResponse,
    summary="Update a website"
)
def update_website(
    website_id: UUID,
    website_data: WebsiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WebsiteResponse:
    """
    Update an existing website.
    
    Only updates the fields that are provided.
    Returns 404 if the website doesn't exist or doesn't belong to the user's chatbot.
    """
    return WebsiteController.update_website(
        db=db,
        website_id=website_id,
        website_data=website_data,
        current_user=current_user
    )


@router.delete(
    "/{website_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a website"
)
def delete_website(
    website_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Delete a website (soft delete).
    
    The website will be marked as inactive but not removed from the database.
    Returns 404 if the website doesn't exist or doesn't belong to the user's chatbot.
    """
    return WebsiteController.delete_website(
        db=db,
        website_id=website_id,
        current_user=current_user
    )
