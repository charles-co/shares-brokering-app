from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DDL, Column, ForeignKey, Integer, event, func
from sqlalchemy.orm import RelationshipProperty
from sqlmodel import DateTime, Field, Relationship, SQLModel, UniqueConstraint


class User(
    SQLModel,
    table=True,
):

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
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
        default=None,
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            server_onupdate=func.now(),
        ),
        default=None,
    )
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


class Rate(SQLModel, table=True):

    __table_args__ = (UniqueConstraint("currency"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    base: str
    currency: str
    date: str
    rate: float


event.listen(
    Company.__table__,
    "after_create",
    DDL(
        """
            CREATE TRIGGER updated_at_trigger
            AFTER UPDATE OF name, currency, price, available_shares, symbol
            ON company
            FOR EACH ROW
            BEGIN
                UPDATE company
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = new.id;
            END;
        """
    ),
)

event.listen(
    Rate.__table__,
    "after_create",
    DDL(
        """
            CREATE TRIGGER updated_rate_trigger
            AFTER UPDATE OF rate
            ON rate
            BEGIN
                UPDATE company
                SET price = ROUND(((new.rate / old.rate) * price), 2)
                WHERE currency = old.currency;
            END;
        """
    ),
)
