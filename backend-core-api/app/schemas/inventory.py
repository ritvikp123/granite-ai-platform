from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class InventoryResponse(BaseModel):
    id: int
    sku: str
    name: str
    available_quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)
