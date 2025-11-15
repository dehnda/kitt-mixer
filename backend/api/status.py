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


@router.get("/diagnostics")
async def get_diagnostics(db_service, arduino_service):
    """Run system diagnostics"""
    try:
        # Check database
        try:
            pumps = db_service.get_all_pumps()
            db_ok = True
        except Exception:
            db_ok = False
            pumps = []

        # Check Arduino
        arduino_ok = arduino_service.is_connected

        # Check pumps with liquid
        pumps_with_liquid = len([p for p in pumps if p.get('liquid_id')])

        return {
            "database": "OK" if db_ok else "ERROR",
            "arduino": "CONNECTED" if arduino_ok else "DISCONNECTED",
            "total_pumps": len(pumps),
            "pumps_ok": pumps_with_liquid,
            "timestamp": "2025-11-15T00:00:00Z"
        }

    except Exception as e:
        return {
            "database": "ERROR",
            "arduino": "ERROR",
            "total_pumps": 0,
            "pumps_ok": 0,
            "error": str(e)
        }
