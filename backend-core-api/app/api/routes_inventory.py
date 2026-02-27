from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryResponse

router = APIRouter(tags=["inventory"])


@router.get("/inventory", response_model=list[InventoryResponse])
def list_inventory(db: Session = Depends(get_db_session)) -> list[Inventory]:
    return db.query(Inventory).order_by(Inventory.id.asc()).all()
