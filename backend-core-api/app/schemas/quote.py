from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class QuoteDraftRequest(BaseModel):
    inventory_id: int
    quantity: int = Field(gt=0)


class QuoteApproveRequest(BaseModel):
    quote_id: int


class QuoteResponse(BaseModel):
    id: int
    inventory_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)
