from fastapi import APIRouter

from app.api.authentication import authentication
from app.api.company import company
from app.api.shares import shares

api_router = APIRouter()

api_router.include_router(authentication.router, prefix="/account", tags=["auth"])
api_router.include_router(company.router, prefix="/company", tags=["company"])
api_router.include_router(shares.router, prefix="/shares", tags=["shares"])
# print(api_router.routes[0].__dict__)
