from fastapi import APIRouter
from models import MixerStatus, ApiResponse
from typing import List

router = APIRouter(prefix="/status", tags=["Status"])


@router.get("", response_model=MixerStatus)
async def get_status(mixer_service):
    """Get current mixer status"""
    status_data = mixer_service.get_status()
    return MixerStatus(**status_data)


@router.post("/cancel", response_model=ApiResponse)
async def cancel_mixing(mixer_service):
    """Cancel current mixing operation"""
    success = mixer_service.cancel_mixing()
    
    if not success:
        return ApiResponse(
            success=False,
            message="No active mixing operation to cancel"
        )
    
    return ApiResponse(
        success=True,
        message="Mixing operation cancelled"
    )


@router.post("/emergency-stop", response_model=ApiResponse)
async def emergency_stop(mixer_service):
    """Emergency stop - immediately stop all pumps"""
    mixer_service.emergency_stop()
    
    return ApiResponse(
        success=True,
        message="Emergency stop activated - all pumps stopped"
    )
