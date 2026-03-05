"""
Service layer for website business logic.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.website import Website
from app.models.chatbot import Chatbot
from app.schemas.website_schema import WebsiteCreate, WebsiteUpdate


class WebsiteService:
    """Service for website-related operations."""
    
    @staticmethod
    def create_website(
        db: Session,
        website_data: WebsiteCreate,
        owner_id: UUID
    ) -> Website:
        """
        Create a new website for a chatbot.
        
        Args:
            db: Database session
            website_data: Website creation data
            owner_id: ID of the user creating the website
            
        Returns:
            Created website instance
            
        Raises:
            SQLAlchemyError: If database operation fails
            ValueError: If chatbot doesn't exist or doesn't belong to user
        """
        # Verify the chatbot exists and belongs to the user
        chatbot = db.query(Chatbot).filter(
            Chatbot.id == website_data.chatbot_id,
            Chatbot.owner_id == owner_id,
            Chatbot.is_active == True
        ).first()
        
        if not chatbot:
            raise ValueError("Chatbot not found or access denied")
        
        try:
            website = Website(
                name=website_data.name,
                url=website_data.url,
                chatbot_id=website_data.chatbot_id,
                description=website_data.description
            )
            
            db.add(website)
            db.commit()
            db.refresh(website)
            
            return website
            
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    @staticmethod
    def get_website_by_id(
        db: Session,
        website_id: UUID,
        owner_id: UUID
    ) -> Optional[Website]:
        """
        Get a website by ID, ensuring it belongs to a chatbot owned by the user.
        
        Args:
            db: Database session
            website_id: ID of the website to retrieve
            owner_id: ID of the requesting user
            
        Returns:
            Website instance if found and accessible, None otherwise
        """
        return db.query(Website).join(
            Chatbot, Website.chatbot_id == Chatbot.id
        ).filter(
            Website.id == website_id,
            Chatbot.owner_id == owner_id,
            Website.is_active == True
        ).first()
    
    @staticmethod
    def get_websites_by_chatbot(
        db: Session,
        chatbot_id: UUID,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Website]:
        """
        Get all websites for a specific chatbot.
        
        Args:
            db: Database session
            chatbot_id: ID of the chatbot
            owner_id: ID of the user
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of website instances
        """
        # Verify chatbot ownership
        chatbot = db.query(Chatbot).filter(
            Chatbot.id == chatbot_id,
            Chatbot.owner_id == owner_id,
            Chatbot.is_active == True
        ).first()
        
        if not chatbot:
            return []
        
        return db.query(Website).filter(
            Website.chatbot_id == chatbot_id,
            Website.is_active == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_user_websites(
        db: Session,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> list[Website]:
        """
        Get all websites across all chatbots owned by the user.
        
        Args:
            db: Database session
            owner_id: ID of the user
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of website instances
        """
        return db.query(Website).join(
            Chatbot, Website.chatbot_id == Chatbot.id
        ).filter(
            Chatbot.owner_id == owner_id,
            Website.is_active == True
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def count_chatbot_websites(
        db: Session,
        chatbot_id: UUID,
        owner_id: UUID
    ) -> int:
        """
        Count total websites for a chatbot.
        
        Args:
            db: Database session
            chatbot_id: ID of the chatbot
            owner_id: ID of the user
            
        Returns:
            Total count of active websites
        """
        # Verify chatbot ownership
        chatbot = db.query(Chatbot).filter(
            Chatbot.id == chatbot_id,
            Chatbot.owner_id == owner_id,
            Chatbot.is_active == True
        ).first()
        
        if not chatbot:
            return 0
        
        return db.query(Website).filter(
            Website.chatbot_id == chatbot_id,
            Website.is_active == True
        ).count()
    
    @staticmethod
    def count_user_websites(db: Session, owner_id: UUID) -> int:
        """
        Count total websites across all chatbots for a user.
        
        Args:
            db: Database session
            owner_id: ID of the user
            
        Returns:
            Total count of active websites
        """
        return db.query(Website).join(
            Chatbot, Website.chatbot_id == Chatbot.id
        ).filter(
            Chatbot.owner_id == owner_id,
            Website.is_active == True
        ).count()
    
    @staticmethod
    def update_website(
        db: Session,
        website_id: UUID,
        owner_id: UUID,
        website_data: WebsiteUpdate
    ) -> Optional[Website]:
        """
        Update a website.
        
        Args:
            db: Database session
            website_id: ID of the website to update
            owner_id: ID of the requesting user
            website_data: Update data
            
        Returns:
            Updated website instance if found and accessible
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        website = WebsiteService.get_website_by_id(db, website_id, owner_id)
        
        if not website:
            return None
        
        try:
            # Update only provided fields
            update_data = website_data.model_dump(exclude_unset=True)
            
            for field, value in update_data.items():
                setattr(website, field, value)
            
            db.commit()
            db.refresh(website)
            
            return website
            
        except SQLAlchemyError as e:
            db.rollback()
            raise e
    
    @staticmethod
    def delete_website(
        db: Session,
        website_id: UUID,
        owner_id: UUID
    ) -> bool:
        """
        Delete (soft delete) a website.
        
        Args:
            db: Database session
            website_id: ID of the website to delete
            owner_id: ID of the requesting user
            
        Returns:
            True if deleted successfully, False if not found
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        website = WebsiteService.get_website_by_id(db, website_id, owner_id)
        
        if not website:
            return False
        
        try:
            # Soft delete
            website.is_active = False
            db.commit()
            
            return True
            
        except SQLAlchemyError as e:
            db.rollback()
            raise e
