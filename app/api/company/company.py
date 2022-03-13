from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import and_, col, or_

from app.db.database import get_session
from app.models import Company
from app.schemas.company import CompanyCreateSchema, CompanyModelSchema

router = APIRouter()


@router.post("", response_model=CompanyModelSchema, status_code=status.HTTP_201_CREATED)
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


@router.get("", response_model=List[CompanyModelSchema], status_code=status.HTTP_200_OK)
async def get_companies(
    name: Optional[str] = Query(None),
    currency: Optional[str] = Query(None),
    price: Optional[float] = Query(None),
    price__lt: Optional[float] = Query(None),
    price__gt: Optional[float] = Query(None),
    available: Optional[int] = Query(None),
    available__lt: Optional[int] = Query(None),
    available__gt: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_session),
) -> List[CompanyModelSchema]:

    _filter = []

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

    statement = select(Company).where(and_(*_filter))
    companies = await db.execute(statement)
    result = companies.scalars().all()
    return result


@router.get(
    "/{company_id}", response_model=CompanyModelSchema, status_code=status.HTTP_200_OK
)
async def get_company_by_id(
    company_id: int, db: AsyncSession = Depends(get_session)
) -> CompanyModelSchema:

    company = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    return CompanyModelSchema.from_orm(company)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
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
    "/{company_id}", response_model=CompanyModelSchema, status_code=status.HTTP_200_OK
)
async def update_company_by_id(
    company_id: int,
    company: CompanyCreateSchema,
    db: AsyncSession = Depends(get_session),
) -> CompanyModelSchema:

    company_db = await db.get(Company, company_id)
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    company_db.name = company.name
    company_db.symbol = company.symbol
    company_db.currency = company.currency
    company_db.price = company.price
    company_db.available_shares = company.available_shares

    db.add(company_db)
    await db.commit()
    await db.refresh(company_db)
    return CompanyModelSchema.from_orm(company_db)
