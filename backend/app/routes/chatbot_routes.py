"""
API routes for chatbot management.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.controllers.chatbot_controller import ChatbotController
from app.models.user import User
from app.schemas.chatbot_schema import (
    ChatbotCreate,
    ChatbotListResponse,
    ChatbotResponse,
    ChatbotUpdate,
)
from app.utils.dependencies import get_current_user, get_db

router = APIRouter(
    prefix="/chatbots",
    tags=["Chatbots"]
)


@router.post(
    "",
    response_model=ChatbotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chatbot"
)
def create_chatbot(
    chatbot_data: ChatbotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ChatbotResponse:
    """
    Create a new chatbot for the authenticated user.
    
    - **name**: Name of the chatbot (required)
    - **description**: Optional description of the chatbot
    """
    return ChatbotController.create_chatbot(
        db=db,
        chatbot_data=chatbot_data,
        current_user=current_user
    )


@router.get(
    "",
    response_model=ChatbotListResponse,
    summary="List all chatbots"
)
def list_chatbots(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ChatbotListResponse:
    """
    Get all chatbots for the authenticated user.
    
    Supports pagination with skip and limit parameters.
    """
    return ChatbotController.list_chatbots(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit
    )


@router.get(
    "/{chatbot_id}",
    response_model=ChatbotResponse,
    summary="Get a chatbot by ID"
)
def get_chatbot(
    chatbot_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ChatbotResponse:
    """
    Get a specific chatbot by ID.
    
    Returns 404 if the chatbot doesn't exist or doesn't belong to the user.
    """
    return ChatbotController.get_chatbot(
        db=db,
        chatbot_id=chatbot_id,
        current_user=current_user
    )


@router.put(
    "/{chatbot_id}",
    response_model=ChatbotResponse,
    summary="Update a chatbot"
)
def update_chatbot(
    chatbot_id: UUID,
    chatbot_data: ChatbotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> ChatbotResponse:
    """
    Update an existing chatbot.
    
    Only updates the fields that are provided.
    Returns 404 if the chatbot doesn't exist or doesn't belong to the user.
    """
    return ChatbotController.update_chatbot(
        db=db,
        chatbot_id=chatbot_id,
        chatbot_data=chatbot_data,
        current_user=current_user
    )


@router.delete(
    "/{chatbot_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a chatbot"
)
def delete_chatbot(
    chatbot_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict:
    """
    Delete a chatbot (soft delete).
    
    The chatbot will be marked as inactive but not removed from the database.
    Returns 404 if the chatbot doesn't exist or doesn't belong to the user.
    """
    return ChatbotController.delete_chatbot(
        db=db,
        chatbot_id=chatbot_id,
        current_user=current_user
    )
