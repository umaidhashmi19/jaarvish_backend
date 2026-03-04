"""
Service layer for chatbot business logic.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.chatbot import Chatbot
from app.schemas.chatbot_schema import ChatbotCreate, ChatbotUpdate


class ChatbotService:
    """Service for chatbot-related operations."""
    
    @staticmethod
    def create_chatbot(
        db: Session,
        chatbot_data: ChatbotCreate,
        owner_id: UUID
    ) -> Chatbot:
        """
        Create a new chatbot for a user.
        
        Args:
            db: Database session
            chatbot_data: Chatbot creation data
            owner_id: ID of the user creating the chatbot
            
        Returns:
            Created chatbot instance
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            chatbot = Chatbot(
                name=chatbot_data.name,
                description=chatbot_data.description,
                owner_id=owner_id
            )
            
            db.add(chatbot)
            db.commit()
            db.refresh(chatbot)
            
            return chatbot
            
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    @staticmethod
    def get_chatbot_by_id(
        db: Session,
        chatbot_id: UUID,
        owner_id: UUID
    ) -> Optional[Chatbot]:
        """
        Get a chatbot by ID, ensuring it belongs to the requesting user.
        
        Args:
            db: Database session
            chatbot_id: ID of the chatbot to retrieve
            owner_id: ID of the requesting user
            
        Returns:
            Chatbot instance if found and owned by user, None otherwise
        """
        return db.query(Chatbot).filter(
            Chatbot.id == chatbot_id,
            Chatbot.owner_id == owner_id,
            Chatbot.is_active == True
        ).first()
    
    @staticmethod
    def get_user_chatbots(
        db: Session,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Chatbot]:
        """
        Get all chatbots for a user.
        
        Args:
            db: Database session
            owner_id: ID of the user
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of chatbot instances
        """
        return db.query(Chatbot).filter(
            Chatbot.owner_id == owner_id,
            Chatbot.is_active == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_user_chatbots(db: Session, owner_id: UUID) -> int:
        """
        Count total chatbots for a user.
        
        Args:
            db: Database session
            owner_id: ID of the user
            
        Returns:
            Total count of active chatbots
        """
        return db.query(Chatbot).filter(
            Chatbot.owner_id == owner_id,
            Chatbot.is_active == True
        ).count()
    
    @staticmethod
    def update_chatbot(
        db: Session,
        chatbot_id: UUID,
        owner_id: UUID,
        chatbot_data: ChatbotUpdate
    ) -> Optional[Chatbot]:
        """
        Update a chatbot.
        
        Args:
            db: Database session
            chatbot_id: ID of the chatbot to update
            owner_id: ID of the requesting user
            chatbot_data: Update data
            
        Returns:
            Updated chatbot instance if found and owned by user
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        chatbot = ChatbotService.get_chatbot_by_id(db, chatbot_id, owner_id)
        
        if not chatbot:
            return None
        
        try:
            # Update only provided fields
            update_data = chatbot_data.model_dump(exclude_unset=True)
            
            for field, value in update_data.items():
                setattr(chatbot, field, value)
            
            db.commit()
            db.refresh(chatbot)
            
            return chatbot
            
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    @staticmethod
    def delete_chatbot(
        db: Session,
        chatbot_id: UUID,
        owner_id: UUID
    ) -> bool:
        """
        Delete (soft delete) a chatbot.
        
        Args:
            db: Database session
            chatbot_id: ID of the chatbot to delete
            owner_id: ID of the requesting user
            
        Returns:
            True if deleted successfully, False if not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        chatbot = ChatbotService.get_chatbot_by_id(db, chatbot_id, owner_id)
        
        if not chatbot:
            return False
        
        try:
            # Soft delete
            chatbot.is_active = False
            db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            raise e
