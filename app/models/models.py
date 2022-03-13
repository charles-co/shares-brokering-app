from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import RelationshipProperty
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint


class User(SQLModel, table=True):

    __table_args__ = (UniqueConstraint("username"), UniqueConstraint("email"))

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(..., index=True, min_length=2)
    hashed_password: str = Field(...)
    email: Optional[str] = ""
    full_name: Optional[str] = ""
    disabled: Optional[bool] = False
    shares: List["ShareHolder"] = Relationship(
        sa_relationship=RelationshipProperty(
            "ShareHolder",
            back_populates="user",
            cascade="all, delete",
            lazy="subquery",
        )
    )


class Company(SQLModel, table=True):

    __table_args__ = (
        UniqueConstraint("symbol"),
        UniqueConstraint("name"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., index=True, min_length=2)
    symbol: str = Field(..., index=True)
    currency: str = Field(...)
    price: float = Field(
        ...,
        ge=0.00,
        index=True,
    )
    available_shares: int = Field(..., gt=-1)
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    share_holders: List["ShareHolder"] = Relationship(
        sa_relationship=RelationshipProperty(
            "ShareHolder",
            back_populates="company",
            cascade="all, delete",
            lazy="subquery",
        )
    )


class ShareHolder(SQLModel, table=True):

    __table_args__ = (UniqueConstraint("user_id", "company_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("user.id", ondelete="CASCADE"), default=None
        )
    )
    company_id: Optional[int] = Field(
        sa_column=Column(
            Integer, ForeignKey("company.id", ondelete="CASCADE"), default=None
        )
    )
    user: Optional[User] = Relationship(back_populates="shares")
    company: Optional[Company] = Relationship(
        sa_relationship=RelationshipProperty(
            "Company",
            back_populates="share_holders",
            lazy="subquery",
        )
    )
    quantity: float = Field(0.00, gt=-1)
