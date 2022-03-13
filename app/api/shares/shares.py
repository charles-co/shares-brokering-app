from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.auth import get_current_active_user
from app.db.database import get_session
from app.models import Company, ShareHolder, User
from app.schemas.user import UserModelSchema

router = APIRouter()


@router.post(
    "/buy/{company_id}", response_model=UserModelSchema, status_code=status.HTTP_200_OK
)
async def buy(
    company_id: int,
    quantity: int = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_session),
) -> UserModelSchema:
    company = await db.get(Company, company_id)

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )

    if company.available_shares == 0 or company.available_shares < quantity:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Not enough company shares",
        )

    statement = select(ShareHolder).where(
        ShareHolder.company_id == company.id, ShareHolder.user_id == current_user.id
    )
    share_holder = await db.execute(statement)

    result: ShareHolder = share_holder.scalar_one_or_none()

    company.available_shares -= quantity
    if result:
        result.quantity += quantity
        db.add(result)
    else:
        share_holder = ShareHolder(
            quantity=quantity, user_id=current_user.id, company_id=company.id
        )
        db.add(share_holder)

    await db.commit()
    current_user = await db.get(User, current_user.id)
    return UserModelSchema.from_orm(current_user)
