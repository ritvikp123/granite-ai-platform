from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user_id, get_db_session
from app.core.errors import APIError
from app.models.inventory import Inventory
from app.models.quote import Quote
from app.schemas.quote import QuoteApproveRequest, QuoteDraftRequest, QuoteResponse
from app.services.audit import log_audit

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("/draft", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
def draft_quote(
    payload: QuoteDraftRequest,
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
) -> Quote:
    item = db.query(Inventory).filter(Inventory.id == payload.inventory_id).first()
    if not item:
        raise APIError("Inventory item not found", status.HTTP_404_NOT_FOUND)
    if item.available_quantity < payload.quantity:
        raise APIError("Insufficient inventory for quote", status.HTTP_409_CONFLICT)

    unit_price = Decimal(item.unit_price)
    total_price = unit_price * payload.quantity
    quote = Quote(
        inventory_id=item.id,
        quantity=payload.quantity,
        unit_price=unit_price,
        total_price=total_price,
        status="draft",
        created_by_user_id=user_id,
    )
    db.add(quote)
    db.flush()
    log_audit(
        db,
        actor_user_id=user_id,
        action="generate_quote_draft",
        resource_type="quote",
        resource_id=str(quote.id),
        details={"inventory_id": item.id, "quantity": payload.quantity},
    )
    db.commit()
    db.refresh(quote)
    return quote


@router.post("/approve", response_model=QuoteResponse)
def approve_quote(
    payload: QuoteApproveRequest,
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
) -> Quote:
    quote = db.query(Quote).filter(Quote.id == payload.quote_id).first()
    if not quote:
        raise APIError("Quote not found", status.HTTP_404_NOT_FOUND)
    if quote.status == "approved":
        raise APIError("Quote already approved", status.HTTP_409_CONFLICT)

    quote.status = "approved"
    quote.approved_by_user_id = user_id
    quote.approved_at = datetime.utcnow()
    db.flush()
    log_audit(
        db,
        actor_user_id=user_id,
        action="approve_quote",
        resource_type="quote",
        resource_id=str(quote.id),
        details={"approved_at": quote.approved_at.isoformat()},
    )
    db.commit()
    db.refresh(quote)
    return quote
