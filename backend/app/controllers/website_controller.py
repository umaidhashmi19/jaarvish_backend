"""
Controller for website endpoints.
"""

from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.website_schema import (
    WebsiteCreate,
    WebsiteListResponse,
    WebsiteResponse,
    WebsiteUpdate,
)
from app.services.website_service import WebsiteService


class WebsiteController:
    """Controller for handling website-related operations."""
    
    @staticmethod
    def create_website(
        db: Session,
        website_data: WebsiteCreate,
        current_user: User
    ) -> WebsiteResponse:
        """
        Create a new website.
        
        Args:
            db: Database session
            website_data: Website creation data
            current_user: Authenticated user
            
        Returns:
            Created website response
            
        Raises:
            HTTPException: If creation fails or chatbot not found
        """
        try:
            website = WebsiteService.create_website(
                db=db,
                website_data=website_data,
                owner_id=current_user.id
            )
            
            return WebsiteResponse.model_validate(website)
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create website: {str(e)}"
            )
    
    @staticmethod
    def get_website(
        db: Session,
        website_id: UUID,
        current_user: User
    ) -> WebsiteResponse:
        """
        Get a website by ID.
        
        Args:
            db: Database session
            website_id: ID of the website
            current_user: Authenticated user
            
        Returns:
            Website response
            
        Raises:
            HTTPException: If website not found or access denied
        """
        website = WebsiteService.get_website_by_id(
            db=db,
            website_id=website_id,
            owner_id=current_user.id
        )
        
        if not website:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Website not found"
            )
        
        return WebsiteResponse.model_validate(website)
    
    @staticmethod
    def list_websites_by_chatbot(
        db: Session,
        chatbot_id: UUID,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> WebsiteListResponse:
        """
        List all websites for a specific chatbot.
        
        Args:
            db: Database session
            chatbot_id: ID of the chatbot
            current_user: Authenticated user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of websites with total count
        """
        websites = WebsiteService.get_websites_by_chatbot(
            db=db,
            chatbot_id=chatbot_id,
            owner_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        total = WebsiteService.count_chatbot_websites(
            db=db,
            chatbot_id=chatbot_id,
            owner_id=current_user.id
        )
        
        return WebsiteListResponse(
            websites=[WebsiteResponse.model_validate(w) for w in websites],
            total=total
        )
    
    @staticmethod
    def list_all_websites(
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> WebsiteListResponse:
        """
        List all websites across all chatbots for the current user.
        
        Args:
            db: Database session
            current_user: Authenticated user
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of websites with total count
        """
        websites = WebsiteService.get_all_user_websites(
            db=db,
            owner_id=current_user.id,
            skip=skip,
            limit=limit
        )
        
        total = WebsiteService.count_user_websites(
            db=db,
            owner_id=current_user.id
        )
        
        return WebsiteListResponse(
            websites=[WebsiteResponse.model_validate(w) for w in websites],
            total=total
        )
    
    @staticmethod
    def update_website(
        db: Session,
        website_id: UUID,
        website_data: WebsiteUpdate,
        current_user: User
    ) -> WebsiteResponse:
        """
        Update a website.
        
        Args:
            db: Database session
            website_id: ID of the website to update
            website_data: Update data
            current_user: Authenticated user
            
        Returns:
            Updated website response
            
        Raises:
            HTTPException: If website not found or update fails
        """
        try:
            website = WebsiteService.update_website(
                db=db,
                website_id=website_id,
                owner_id=current_user.id,
                website_data=website_data
            )
            
            if not website:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Website not found"
                )
            
            return WebsiteResponse.model_validate(website)
            
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update website: {str(e)}"
            )
    
    @staticmethod
    def delete_website(
        db: Session,
        website_id: UUID,
        current_user: User
    ) -> dict:
        """
        Delete a website.
        
        Args:
            db: Database session
            website_id: ID of the website to delete
            current_user: Authenticated user
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If website not found or deletion fails
        """
        try:
            deleted = WebsiteService.delete_website(
                db=db,
                website_id=website_id,
                owner_id=current_user.id
            )
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Website not found"
                )
            
            return {
                "success": True,
                "message": "Website deleted successfully"
            }
            
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete website: {str(e)}"
            )
