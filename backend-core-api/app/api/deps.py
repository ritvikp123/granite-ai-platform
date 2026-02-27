from fastapi import Depends, Request
from sqlalchemy.orm import Session
from starlette import status

from app.core.errors import APIError
from app.db.session import get_db


def get_db_session(db: Session = Depends(get_db)) -> Session:
    return db


def get_current_user_id(request: Request) -> int:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        raise APIError("Authentication required", status.HTTP_401_UNAUTHORIZED)
    return user_id
