from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.controllers.auth_controller import AuthController
from app.db import get_db
from app.models.user import User
from app.schemas.auth_schema import (
    AuthResponse,
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.utils.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# POST /auth/signup
# ---------------------------------------------------------------------------

@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=201,
    summary="Register a new user",
)
def signup(
    payload: SignupRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Create a new user account.

    Returns a JWT access + refresh token pair alongside the user profile.
    """
    return AuthController.signup(payload, db)


# ---------------------------------------------------------------------------
# POST /auth/login  (JSON body)
# ---------------------------------------------------------------------------

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login with email and password (JSON)",
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    """
    Authenticate using a JSON request body.

    Returns a JWT access + refresh token pair alongside the user profile.
    """
    return AuthController.login(payload, db)


# ---------------------------------------------------------------------------
# POST /auth/login/form  (OAuth2 Password Flow — for Swagger UI)
# ---------------------------------------------------------------------------

@router.post(
    "/login/form",
    response_model=TokenResponse,
    summary="Login via OAuth2 Password Flow (form data)",
    include_in_schema=True,
)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    OAuth2 Password Flow endpoint — accepts ``application/x-www-form-urlencoded``.

    The ``username`` field should contain the user's **email address**.
    This endpoint is used automatically by the Swagger UI *Authorize* button.
    """
    return AuthController.login_form(form_data, db)


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------

@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
)
def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Exchange a valid refresh token for a new access + refresh token pair.
    """
    return AuthController.refresh(refresh_token, db)


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Return the profile of the currently authenticated user.

    Requires a valid Bearer access token.
    """
    return AuthController.me(current_user)