from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_db_session
from app.core.errors import APIError
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db_session)) -> TokenResponse:
    user = db.query(User).filter(User.username == payload.username, User.is_active.is_(True)).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise APIError("Invalid username or password", status.HTTP_401_UNAUTHORIZED)

    token = create_access_token(user.username)
    return TokenResponse(access_token=token)
