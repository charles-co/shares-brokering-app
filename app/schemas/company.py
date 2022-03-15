from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, confloat, conint, constr, validator

from app.api.shares.constants import Currency

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


class CompanySchema(BaseModel):
    name: str = Field(..., min_length=2)
    symbol: constr(strip_whitespace=True, min_length=2) = Field(...)
    price: confloat(ge=0, multiple_of=0.01) = Field(..., description=("Per unit"))
    available_shares: conint(ge=0) = Field(...)
    _upper_name = validator("name", allow_reuse=True, check_fields=False)(change_case)
    _upper_symbol = validator("symbol", allow_reuse=True, check_fields=False)(
        change_case
    )

    class Config:
        orm_mode = True
        use_enum_values = True


class CompanyPatchSchema(BaseModel):

    name: Optional[str] = Field(None, min_length=2)
    symbol: constr(strip_whitespace=True, min_length=2) = Field(None)
    price: confloat(ge=0, multiple_of=0.01) = Field(None)
    available_shares: conint(ge=0) = Field(None)


class CompanyCreateSchema(CompanySchema):

    currency: Currency = Field(...)
    _upper_currency = validator("currency", allow_reuse=True, check_fields=False)(
        change_case
    )
