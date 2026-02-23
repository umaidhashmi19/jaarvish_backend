from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth_schema import (
    AuthResponse,
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def _build_tokens(user: User) -> TokenResponse:
    """Create a fresh access + refresh token pair for *user*."""
    access_token = create_access_token(
        subject=str(user.id),
        extra_claims={"email": user.email},
    )
    refresh_token = create_refresh_token(subject=str(user.id))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def register_user(payload: SignupRequest, db: Session) -> AuthResponse:
    """
    Create a new user account.

    Raises:
        409 — if the email or username is already taken.
    """
    # Check uniqueness
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this username already exists.",
        )

    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        tokens=_build_tokens(user),
        user=UserResponse.model_validate(user),
    )


def login_user(payload: LoginRequest, db: Session) -> AuthResponse:
    """
    Authenticate with email + password.

    Raises:
        401 — on invalid credentials or inactive account.
    """
    user: User | None = db.query(User).filter(User.email == payload.email).first()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact support.",
        )

    return AuthResponse(
        tokens=_build_tokens(user),
        user=UserResponse.model_validate(user),
    )


def refresh_access_token(refresh_token: str, db: Session) -> TokenResponse:
    """
    Issue a new access token from a valid refresh token.

    Raises:
        401 — if the refresh token is invalid, expired, or of the wrong type.
    """
    from jose import JWTError

    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise credentials_exc
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user: User | None = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exc

    return TokenResponse(
        access_token=create_access_token(
            subject=str(user.id),
            extra_claims={"email": user.email},
        ),
        refresh_token=create_refresh_token(subject=str(user.id)),
    )