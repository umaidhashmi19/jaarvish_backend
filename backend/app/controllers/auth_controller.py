"""
Auth controller — thin layer between routes and the auth service.

Responsibilities:
  • Accept validated request data and a DB session.
  • Delegate business logic to ``auth_service``.
  • Return structured response objects ready for serialisation.
"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.auth_schema import (
    AuthResponse,
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import (
    login_user,
    refresh_access_token,
    register_user,
)
from app.utils.dependencies import get_current_active_user


class AuthController:
    # ------------------------------------------------------------------
    # Sign-up
    # ------------------------------------------------------------------

    @staticmethod
    def signup(
        payload: SignupRequest,
        db: Session = Depends(get_db),
    ) -> AuthResponse:
        """Register a new user and return tokens + profile."""
        return register_user(payload, db)

    # ------------------------------------------------------------------
    # Login — JSON body
    # ------------------------------------------------------------------

    @staticmethod
    def login(
        payload: LoginRequest,
        db: Session = Depends(get_db),
    ) -> AuthResponse:
        """Authenticate via JSON body and return tokens + profile."""
        return login_user(payload, db)

    # ------------------------------------------------------------------
    # Login — OAuth2 form (used by Swagger UI / OpenAPI clients)
    # ------------------------------------------------------------------

    @staticmethod
    def login_form(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db),
    ) -> TokenResponse:
        """
        OAuth2 Password Flow — accepts ``application/x-www-form-urlencoded``.

        ``username`` in the form maps to the user's *email* field.
        Returns only the token pair (no user profile) to match the OAuth2 spec.
        """
        auth = login_user(
            LoginRequest(email=form_data.username, password=form_data.password),
            db,
        )
        return auth.tokens

    # ------------------------------------------------------------------
    # Token refresh
    # ------------------------------------------------------------------

    @staticmethod
    def refresh(
        refresh_token: str,
        db: Session = Depends(get_db),
    ) -> TokenResponse:
        """Exchange a valid refresh token for a new token pair."""
        return refresh_access_token(refresh_token, db)

    # ------------------------------------------------------------------
    # Current user
    # ------------------------------------------------------------------

    @staticmethod
    def me(
        current_user: User = Depends(get_current_active_user),
    ) -> UserResponse:
        """Return the profile of the currently authenticated user."""
        return UserResponse.model_validate(current_user)