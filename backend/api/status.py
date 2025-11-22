from fastapi import APIRouter, Depends
from models import MixerStatus, ApiResponse, Pump
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/status", tags=["Status"])


class MixerStartRequest(BaseModel):
    """Request to start mixer motor"""
    duration_seconds: Optional[float] = None
    clockwise: bool = True


@router.get("", response_model=MixerStatus)
async def get_status(mixer_service, db_service, gpio_controller):
    """Get current mixer status"""
    status_data = mixer_service.get_status()
    pumps_data = db_service.get_pumps()

    # Convert pump dicts to Pump objects
    pumps = [
        Pump(
            id=p['id'],
            pin=p['pin'],
            ml_per_second=p['ml_per_second'],
            liquid=p.get('liquid'),
            liquid_id=p.get('liquid_id')
        )
        for p in pumps_data
    ]

    return MixerStatus(
        state=status_data['state'],
        is_mixing=status_data['state'] == 'mixing',
        current_cocktail=status_data.get('current_cocktail'),
        progress=status_data.get('progress_percent', 0),
        error_message=status_data.get('error_message'),
        arduino_connected=gpio_controller.is_connected,
        pumps=pumps
    )


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
async def get_diagnostics(db_service, gpio_controller):
    """Run system diagnostics"""
    try:
        # Check database
        try:
            pumps = db_service.get_pumps()
            db_ok = True
        except Exception:
            db_ok = False
            pumps = []

        # Check GPIO Controller
        gpio_ok = gpio_controller.is_connected

        # Check pumps with liquid
        pumps_with_liquid = len([p for p in pumps if p.get('liquid_id')])

        return {
            "database": "OK" if db_ok else "ERROR",
            "gpio": "CONNECTED" if gpio_ok else "DISCONNECTED",
            "total_pumps": len(pumps),
            "pumps_configured": pumps_with_liquid,
            "timestamp": "2025-11-22T00:00:00Z"
        }

    except Exception as e:
        return {
            "database": "ERROR",
            "gpio": "ERROR",
            "total_pumps": 0,
            "pumps_configured": 0,
            "error": str(e)
        }


@router.post("/mixer/start", response_model=ApiResponse)
async def start_mixer_motor(request: MixerStartRequest, mixer_service):
    """Start the mixer motor (stepper)"""
    if not mixer_service.controller.is_connected:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GPIO Controller not connected"
        )
    
    from services.gpio_controller import StepperDirection
    direction = StepperDirection.CLOCKWISE if request.clockwise else StepperDirection.COUNTERCLOCKWISE
    
    success = mixer_service.controller.start_mixer(
        duration_seconds=request.duration_seconds,
        direction=direction
    )
    
    if not success:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start mixer motor"
        )
    
    return ApiResponse(
        success=True,
        message=f"Mixer motor started {'(continuous)' if request.duration_seconds is None else f'for {request.duration_seconds}s'}",
        data={"duration_seconds": request.duration_seconds, "clockwise": request.clockwise}
    )


@router.post("/mixer/stop", response_model=ApiResponse)
async def stop_mixer_motor(mixer_service):
    """Stop the mixer motor"""
    success = mixer_service.controller.stop_mixer()
    
    if not success:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop mixer motor"
        )
    
    return ApiResponse(
        success=True,
        message="Mixer motor stopped"
    )


@router.get("/mixer", response_model=dict)
async def get_mixer_status(mixer_service):
    """Get mixer motor status"""
    status_data = mixer_service.controller.get_status()
    return {
        "running": status_data["mixer"]["running"],
        "step_pin": status_data["mixer"]["step_pin"],
        "dir_pin": status_data["mixer"]["dir_pin"],
        "enable_pin": status_data["mixer"]["enable_pin"]
    }
