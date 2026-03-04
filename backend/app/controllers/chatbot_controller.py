"""
Controller for chatbot endpoints.
"""

from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.chatbot_schema import (
    ChatbotCreate,
    ChatbotListResponse,
    ChatbotResponse,
    ChatbotUpdate,
)
from app.services.chatbot_service import ChatbotService


class ChatbotController:
    """Controller for handling chatbot-related operations."""
    
    @staticmethod
    def create_chatbot(
        db: Session,
        chatbot_data: ChatbotCreate,
        current_user: User
    ) -> ChatbotResponse:
        """
        Create a new chatbot.
        
        Args:
            db: Database session
            chatbot_data: Chatbot creation data
            current_user: Authenticated user
            
        Returns:
            Created chatbot response
            
        Raises:
            HTTPException: If creation fails
        """
        try:
            chatbot = ChatbotService.create_chatbot(
                db=db,
                chatbot_data=chatbot_data,
                owner_id=current_user.id
            )
            
            return ChatbotResponse.model_validate(chatbot)
            
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create chatbot: {str(e)}"
            )
    
    @staticmethod
    def get_chatbot(
        db: Session,
        chatbot_id: UUID,
        current_user: User
    ) -> ChatbotResponse:
        """
        Get a chatbot by ID.
        
        Args:
            db: Database session
            chatbot_id: ID of the chatbot
            current_user: Authenticated user
            
        Returns:
            Chatbot response
            
        Raises:
            HTTPException: If chatbot not found or access denied
        """
        chatbot = ChatbotService.get_chatbot_by_id(
            db=db,
            chatbot_id=chatbot_id,
            owner_id=current_user.id
        )
        
        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot not found"
            )
        
        return ChatbotResponse.model_validate(chatbot)
    
    @staticmethod
    def list_chatbots(
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> ChatbotListResponse:
        """
        List all chatbots for the current user.
        
        Args:
            db: Database session
            current_user: Authenticated user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of chatbots with total count
        """
        chatbots = ChatbotService.get_user_chatbots(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        total = ChatbotService.count_user_chatbots(
            db=db,
            owner_id=current_user.id
        )
        
        return ChatbotListResponse(
            chatbots=[ChatbotResponse.model_validate(c) for c in chatbots],
            total=total
        )
    
    @staticmethod
    def update_chatbot(
        db: Session,
        chatbot_id: UUID,
        chatbot_data: ChatbotUpdate,
        current_user: User
    ) -> ChatbotResponse:
        """
        Update a chatbot.
        
        Args:
            db: Database session
            chatbot_id: ID of the chatbot to update
            chatbot_data: Update data
            current_user: Authenticated user
            
        Returns:
            Updated chatbot response
            
        Raises:
            HTTPException: If chatbot not found or update fails
        """
        try:
            chatbot = ChatbotService.update_chatbot(
                db=db,
                chatbot_id=chatbot_id,
                owner_id=current_user.id,
                chatbot_data=chatbot_data
            )
            
            if not chatbot:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chatbot not found"
                )
            
            return ChatbotResponse.model_validate(chatbot)
            
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update chatbot: {str(e)}"
            )
    
    @staticmethod
    def delete_chatbot(
        db: Session,
        chatbot_id: UUID,
        current_user: User
    ) -> dict:
        """
        Delete a chatbot.
        
        Args:
            db: Database session
            chatbot_id: ID of the chatbot to delete
            current_user: Authenticated user
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If chatbot not found or deletion fails
        """
        try:
            deleted = ChatbotService.delete_chatbot(
                db=db,
                chatbot_id=chatbot_id,
                owner_id=current_user.id
            )
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chatbot not found"
                )
            
            return {"message": "Chatbot deleted successfully"}
            
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete chatbot: {str(e)}"
            )
