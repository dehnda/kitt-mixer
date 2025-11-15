from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from models import Pump, PumpUpdate, ApiResponse
from pydantic import BaseModel

router = APIRouter(prefix="/pumps", tags=["Pumps"])


class PumpConfigUpdate(BaseModel):
    """Update pump configuration"""
    liquid: Optional[str] = None
    ml_per_second: Optional[float] = None


class PumpTestRequest(BaseModel):
    """Request to test pump"""
    duration_seconds: float = 10.0


@router.get("", response_model=List[Pump])
async def get_pumps(db_service):
    """Get all pump configurations"""
    pumps_data = db_service.get_pumps()
    return [Pump(**pump) for pump in pumps_data]


@router.get("/{pump_id}", response_model=Pump)
async def get_pump(pump_id: int, db_service):
    """Get specific pump configuration"""
    pump_data = db_service.get_pump_by_id(pump_id)
    if not pump_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pump {pump_id} not found"
        )
    return Pump(**pump_data)


@router.put("/{pump_id}", response_model=ApiResponse)
async def update_pump(pump_id: int, update: PumpConfigUpdate, db_service):
    """Update pump configuration (liquid and/or flow rate)"""
    # Verify pump exists
    pump = db_service.get_pump_by_id(pump_id)
    if not pump:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pump {pump_id} not found"
        )

    # Update pump configuration
    if update.liquid is not None:
        success = db_service.update_pump_liquid(pump_id, update.liquid if update.liquid else None)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update pump liquid"
            )

    if update.ml_per_second is not None:
        success = db_service.update_pump_flow_rate(pump_id, update.ml_per_second)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update pump flow rate"
            )

    return ApiResponse(
        success=True,
        message=f"Pump {pump_id} updated successfully",
        data={"pump_id": pump_id, "liquid": update.liquid, "ml_per_second": update.ml_per_second}
    )


@router.post("/{pump_id}/test", response_model=ApiResponse)
async def test_pump(pump_id: int, request: PumpTestRequest, db_service, arduino_service):
    """Test pump for calibration (run for specified duration)"""
    # Verify pump exists
    pump = db_service.get_pump_by_id(pump_id)
    if not pump:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pump {pump_id} not found"
        )

    if not arduino_service.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Arduino not connected"
        )

    try:
        # Start pump
        arduino_service.start_pump(pump_id)

        return ApiResponse(
            success=True,
            message=f"Pump {pump_id} started for {request.duration_seconds} seconds",
            data={"pump_id": pump_id, "duration": request.duration_seconds}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start pump: {str(e)}"
        )


@router.put("/{pump_id}/liquid", response_model=ApiResponse)
async def update_pump_liquid(pump_id: int, update: PumpUpdate, db_service):
    """Assign or remove liquid from a pump (legacy endpoint)"""
    # Verify pump exists
    pump = db_service.get_pump_by_id(pump_id)
    if not pump:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pump {pump_id} not found"
        )

    # Update pump liquid
    success = db_service.update_pump_liquid(pump_id, update.liquid)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update pump configuration"
        )

    return ApiResponse(
        success=True,
        message=f"Pump {pump_id} updated successfully",
        data={"pump_id": pump_id, "liquid": update.liquid}
    )
