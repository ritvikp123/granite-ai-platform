from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.api.deps import get_current_user_id, get_db_session
from app.core.errors import APIError
from app.models.hold import Hold
from app.models.inventory import Inventory
from app.schemas.hold import HoldCreateRequest, HoldResponse
from app.services.audit import log_audit

router = APIRouter(tags=["holds"])


@router.post("/holds", response_model=HoldResponse, status_code=status.HTTP_201_CREATED)
def create_hold(
    payload: HoldCreateRequest,
    db: Session = Depends(get_db_session),
    user_id: int = Depends(get_current_user_id),
) -> Hold:
    item = db.query(Inventory).filter(Inventory.id == payload.inventory_id).first()
    if not item:
        raise APIError("Inventory item not found", status.HTTP_404_NOT_FOUND)
    if item.available_quantity < payload.quantity:
        raise APIError("Insufficient inventory for hold", status.HTTP_409_CONFLICT)

    item.available_quantity -= payload.quantity
    hold = Hold(
        inventory_id=payload.inventory_id,
        quantity=payload.quantity,
        status="active",
        created_by_user_id=user_id,
    )
    db.add(hold)
    db.flush()
    log_audit(
        db,
        actor_user_id=user_id,
        action="create_hold",
        resource_type="hold",
        resource_id=str(hold.id),
        details={"inventory_id": payload.inventory_id, "quantity": payload.quantity},
    )
    db.commit()
    db.refresh(hold)
    return hold
