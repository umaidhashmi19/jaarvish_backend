from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.auth_schema import TokenData
from app.utils.security import decode_token

# OAuth2PasswordBearer extracts the Bearer token from the Authorization header.
# tokenUrl points to the OAuth2 form-based login endpoint used by Swagger UI.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/form")


def _credentials_exception(
    detail: str = "Could not validate credentials",
) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the JWT, look up the user, and return the ORM instance.
    Raises 401 on any authentication error.
    """
    try:
        payload = decode_token(token)
        user_id: str | None = payload.get("sub")
        token_type: str | None = payload.get("type")
        if user_id is None or token_type != "access":
            raise _credentials_exception()
        token_data = TokenData(sub=user_id, email=payload.get("email"))
    except JWTError:
        raise _credentials_exception()

    user: User | None = db.query(User).filter(User.id == token_data.sub).first()
    if user is None:
        raise _credentials_exception("User not found")
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Extend *get_current_user* — also ensures the account is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive account",
        )
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Require the authenticated user to be a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user