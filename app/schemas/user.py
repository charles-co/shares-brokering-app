from typing import List, Optional

from pydantic import BaseModel, validate_email, validator

from .shares import ShareModelSchema


class UserSchema(BaseModel):

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    # disabled: Optional[bool] = None


class UserRegistrationSchema(UserSchema):

    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

    @validator("email", pre=True)
    def parse_email(cls, email):
        _, email = validate_email(email)
        return email


class UserModelSchema(BaseModel):

    id: Optional[int]
    username: Optional[str]
    disabled: Optional[bool]
    email: Optional[str]
    full_name: Optional[str]
    hashed_password: Optional[str]
    shares: Optional[List[ShareModelSchema]]

    class Config:
        orm_mode = True
