from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class MixerState(str, Enum):
    """Current state of the mixer"""
    IDLE = "idle"
    MIXING = "mixing"
    ERROR = "error"
    PAUSED = "paused"


class Ingredient(BaseModel):
    """Single ingredient in a cocktail"""
    ingredient: str
    amount: float
    unit: str  # Changed to str to allow any unit value


class Cocktail(BaseModel):
    """Cocktail recipe from database"""
    name: str
    timing: Optional[str] = None  # Changed to str to allow any value
    taste: Optional[str] = None
    ingredients: List[Ingredient]
    preparation: Optional[str] = None


class CocktailWithAvailability(Cocktail):
    """Cocktail with availability information"""
    is_available: bool = False
    missing_ingredients: List[str] = Field(default_factory=list)


class Pump(BaseModel):
    """Pump configuration"""
    id: int
    pin: int
    ml_per_second: float
    liquid: Optional[str] = None
    liquid_id: Optional[int] = None


class PumpUpdate(BaseModel):
    """Update pump liquid assignment"""
    liquid_id: Optional[int] = None


class MakeCocktailRequest(BaseModel):
    """Request to make a cocktail"""
    size_multiplier: float = Field(default=1.0, ge=0.5, le=2.0)


class MixerStatus(BaseModel):
    """Current mixer status"""
    state: MixerState
    current_cocktail: Optional[str] = None
    progress_percent: float = Field(default=0, ge=0, le=100)
    error_message: Optional[str] = None


class ApiResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
