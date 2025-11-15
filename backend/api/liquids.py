from fastapi import APIRouter
from typing import List

router = APIRouter(prefix="/liquids", tags=["Liquids"])


@router.get("", response_model=List[str])
async def get_all_liquids(db_service):
    """Get all unique liquids from cocktail database"""
    return db_service.get_all_unique_ingredients()


@router.get("/installed", response_model=List[str])
async def get_installed_liquids(db_service):
    """Get liquids currently installed in pumps"""
    return db_service.get_installed_liquids()
