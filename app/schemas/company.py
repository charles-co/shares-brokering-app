from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, confloat, conint, constr, validator

from .base import change_case


class CompanyModelSchema(BaseModel):

    id: Optional[int]
    name: Optional[str]
    symbol: Optional[str]
    currency: Optional[str]
    price: Optional[float]
    available_shares: Optional[float]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    # share_holders: Optional[List["ShareHolder"]]

    class Config:
        orm_mode = True


class CompanyCreateSchema(BaseModel):

    name: str = Field(..., min_length=2)
    symbol: constr(strip_whitespace=True, min_length=2) = Field(...)
    currency: str = Field(..., min_length=2)
    price: confloat(ge=0, multiple_of=0.01) = Field(...)
    available_shares: conint(ge=0) = Field(...)
    _upper_name = validator("name", allow_reuse=True)(change_case)
    _upper_symbol = validator("symbol", allow_reuse=True)(change_case)
    _upper_currency = validator("currency", allow_reuse=True)(change_case)
