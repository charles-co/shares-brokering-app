from enum import Enum
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import and_, col, or_

from app.api.shares.constants import Currency
from app.api.utils import convert_currency
from app.db.database import get_session
from app.models import Company
from app.schemas.base import ErrorSchema
from app.schemas.company import (
    CompanyCreateSchema,
    CompanyModelSchema,
    CompanyPatchSchema,
    CompanySchema,
)

router = APIRouter()


class Sort(str, Enum):

    asc = "asc"
    desc = "desc"


@router.post(
    "",
    response_model=CompanyModelSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def create_company(
    company: CompanyCreateSchema, db: AsyncSession = Depends(get_session)
) -> CompanyModelSchema:
    try:
        statement = select(Company).where(
            or_(Company.name == company.name, Company.symbol == company.symbol)
        )
        result = await db.execute(statement)
        company = result.one()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company or symbol already exists",
        )
    except NoResultFound:
        company: Company = Company.from_orm(company)
        db.add(company)
        await db.commit()
        await db.refresh(company)
        return CompanyModelSchema.from_orm(company)


@router.get(
    "",
    response_model=List[CompanyModelSchema],
    status_code=status.HTTP_200_OK,
)
async def get_companies(
    name: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    price: Optional[float] = Query(None),
    price__lt: Optional[float] = Query(None),
    price__gt: Optional[float] = Query(None),
    available: Optional[int] = Query(None),
    available__lt: Optional[int] = Query(None),
    available__gt: Optional[int] = Query(None),
    price__sort: Optional[Sort] = Query(None),
    updated: Optional[Sort] = Query(None),
    db: AsyncSession = Depends(get_session),
) -> List[CompanyModelSchema]:

    _filter = []
    order = []

    if name is not None:
        _filter.append(col(Company.name).contains(name))

    if currency is not None:
        _filter.append(col(Company.currency).contains(currency))

    if price is not None and (price__gt is not None or price__lt is not None):

        _filter.append(Company.price == price)

    else:
        if price__gt is not None:
            _filter.append(Company.price > price__gt)
        else:
            if price__lt is not None:
                _filter.append(Company.price < price__lt)

    if available is not None and (
        available__gt is not None or available__lt is not None
    ):
        _filter.append(Company.available_shares == available)

    else:
        if available__gt is not None:
            _filter.append(Company.available_shares > available__gt)
        else:
            if available__lt is not None:
                _filter.append(Company.available_shares < available__lt)

    if price__sort is not None:
        if price__sort.value == "desc":
            order.append(col(Company.price).desc())
        else:
            order.append(col(Company.price).asc())

    if updated is not None:
        if updated.value == "asc":
            order.append(col(Company.updated_at).asc())
        else:
            order.append(col(Company.updated_at).desc())

    statement = select(Company).where(and_(*_filter)).order_by(*order)
    companies = await db.execute(statement)
    result = companies.scalars().all()
    return result


@router.get(
    "/{company_id}",
    response_model=CompanyModelSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def get_company_by_id(
    company_id: int,
    currency: Currency = Query(None),
    db: AsyncSession = Depends(get_session),
) -> CompanyModelSchema:

    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    company = CompanyModelSchema.from_orm(company)
    if currency:
        result = await convert_currency(
            from_=company.currency, to=currency.value, amount=company.price
        )
        company.currency = currency.value
        company.price = result
    return company


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def delete_company_by_id(
    company_id: int, db: AsyncSession = Depends(get_session)
) -> CompanyModelSchema:

    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    await db.delete(company)
    await db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/{company_id}",
    response_model=CompanyModelSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def update_company_by_id(
    company_id: int,
    company: CompanySchema,
    db: AsyncSession = Depends(get_session),
) -> CompanyModelSchema:

    company_db = await db.get(Company, company_id)
    if company_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    company: Company = Company.from_orm(
        company,
        update={
            "currency": company_db.currency,
            "id": company_db.id,
            "created_at": company_db.created_at,
            "updated_at": company_db.updated_at,
        },
    )

    if company != company_db:
        print("---" * 20)
        print("UPDATE MADE ! " * 4)
        print("---" * 20)
        company_db.name = company.name
        company_db.price = company.price
        company_db.available_shares = company.available_shares
        company_db.symbol = company.symbol

        db.add(company_db)
        await db.commit()
        await db.refresh(company_db)

    return CompanyModelSchema.from_orm(company_db)


@router.patch(
    "/{company_id}",
    response_model=CompanyModelSchema,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorSchema},
    },
)
async def patch_update_company_by_id(
    company_id: int,
    company: CompanyPatchSchema,
    db: AsyncSession = Depends(get_session),
) -> CompanyModelSchema:

    company_db = await db.get(Company, company_id)
    if company_db is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    data = company.dict()
    for key in data.keys():
        if data[key] is not None:
            setattr(company_db, key, data[key])

    db.add(company_db)
    await db.commit()
    await db.refresh(company_db)
    return CompanyModelSchema.from_orm(company_db)
