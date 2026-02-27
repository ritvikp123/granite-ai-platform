from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors import (
    APIError,
    api_error_handler,
    http_exception_handler,
    sqlalchemy_error_handler,
    unhandled_exception_handler,
    validation_error_handler,
)
from app.core.rbac import RBACMiddleware
from app.db.base import Base
from app.db.init_db import seed_defaults
from app.db.session import SessionLocal, engine
from app.models import AuditLog, Hold, Inventory, Quote, Role, User  # noqa: F401

settings = get_settings()
app = FastAPI(title=settings.app_name)

# Allow local frontend to call this API in development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RBACMiddleware)
app.include_router(api_router)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_defaults(db)
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
