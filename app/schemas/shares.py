from typing import Optional

from pydantic import BaseModel

from .company import CompanyModelSchema


class ShareModelSchema(BaseModel):

    company: CompanyModelSchema
    quantity: Optional[int]

    class Config:
        orm_mode = True
