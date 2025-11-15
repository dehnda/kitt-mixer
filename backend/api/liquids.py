from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/liquids", tags=["Liquids"])


class Liquid(BaseModel):
    id: int
    name: str


@router.get("", response_model=List[Liquid])
async def get_all_liquids(db_service):
    """Get all unique liquids from cocktail database with IDs"""
    return db_service.get_all_liquids_with_ids()


@router.get("/installed", response_model=List[Liquid])
async def get_installed_liquids(db_service):
    """Get liquids currently installed in pumps with IDs"""
    return db_service.get_installed_liquids_with_ids()
