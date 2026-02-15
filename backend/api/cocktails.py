from fastapi import APIRouter, HTTPException, status
from typing import List
from models import Cocktail, CocktailWithAvailability, MakeCocktailRequest, ApiResponse

router = APIRouter(prefix="/cocktails", tags=["Cocktails"])


@router.get("", response_model=List[CocktailWithAvailability])
async def get_all_cocktails(mixer_service):
    """Get all cocktails with availability information"""
    return mixer_service.get_available_cocktails()


@router.get("/available", response_model=List[CocktailWithAvailability])
async def get_available_cocktails(mixer_service):
    """Get only cocktails that can be made with current liquids"""
    return mixer_service.get_makeable_cocktails()


@router.get("/{cocktail_name}", response_model=CocktailWithAvailability)
async def get_cocktail(cocktail_name: str, mixer_service):
    """Get specific cocktail details"""
    cocktails = mixer_service.get_available_cocktails()

    # Find the cocktail by name
    cocktail_data = next(
        (c for c in cocktails if c.name.lower() == cocktail_name.lower()), None)

    if not cocktail_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cocktail '{cocktail_name}' not found"
        )

    return cocktail_data


@router.post("/{cocktail_name}/make", response_model=ApiResponse)
async def make_cocktail(cocktail_name: str, request: MakeCocktailRequest, mixer_service):
    """Start making a cocktail"""
    # Check if cocktail exists
    can_make, missing = mixer_service.can_make_cocktail(cocktail_name)

    if not can_make:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot make cocktail. Missing ingredients: {', '.join(missing)}"
        )

    # Start making the cocktail
    success = mixer_service.make_cocktail(
        cocktail_name, request.size_multiplier)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=mixer_service.error_message or "Mixer is busy"
        )

    return ApiResponse(
        success=True,
        message=f"Started making {cocktail_name}",
        data={
            "cocktail_name": cocktail_name,
            "size_multiplier": request.size_multiplier
        }
    )
