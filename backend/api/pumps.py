from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from models import Pump, PumpUpdate, ApiResponse
from pydantic import BaseModel

router = APIRouter(prefix="/pumps", tags=["Pumps"])


class PumpConfigUpdate(BaseModel):
    """Update pump configuration"""
    liquid_id: Optional[int] = None
    ml_per_second: Optional[float] = None


class PumpTestRequest(BaseModel):
    """Request to test pump"""
    duration_seconds: float = 10.0


@router.get("", response_model=List[Pump])
async def get_pumps(db_service):
    """Get all pump configurations with liquid IDs"""
    pumps_data = db_service.get_pumps()
    # Add liquid_id to each pump if not present
    for pump in pumps_data:
        if 'liquid_id' not in pump and pump.get('liquid'):
            # Backward compatibility: get ID from name
            pump['liquid_id'] = db_service.get_id_for_liquid(pump['liquid'])
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
    """Update pump configuration (liquid ID and/or flow rate)"""
    # Verify pump exists
    pump = db_service.get_pump_by_id(pump_id)
    if not pump:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pump {pump_id} not found"
        )

    # Update pump configuration
    success = True
    if update.liquid_id is not None:
        success = db_service.update_pump_liquid(pump_id, update.liquid_id)
    if success and update.ml_per_second is not None:
        success = db_service.update_pump_flow_rate(pump_id, update.ml_per_second)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update pump configuration"
        )

    liquid_name = db_service.get_liquid_by_id(update.liquid_id) if update.liquid_id else "pump"
    return ApiResponse(
        success=True,
        message=f"Pump {pump_id} ({liquid_name}) updated successfully"
    )
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


@router.post("/test-all", response_model=ApiResponse)
async def test_all_pumps(request: PumpTestRequest, db_service, arduino_service):
    """Test all pumps sequentially"""
    if not arduino_service.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Arduino not connected"
        )

    try:
        pumps = db_service.get_all_pumps()
        tested = 0

        for pump in pumps:
            try:
                arduino_service.start_pump(pump['id'])
                tested += 1
                # Small delay between pumps
                import time
                time.sleep(0.5)
            except Exception as e:
                print(f"Failed to test pump {pump['id']}: {e}")

        return ApiResponse(
            success=True,
            message=f"Tested {tested}/{len(pumps)} pumps for {request.duration_seconds} seconds each"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test all pumps: {str(e)}"
        )


@router.post("/purge-all", response_model=ApiResponse)
async def purge_all_pumps(request: PumpTestRequest, db_service, arduino_service):
    """Purge all pumps with assigned liquids to clear lines"""
    if not arduino_service.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Arduino not connected"
        )

    try:
        pumps = db_service.get_all_pumps()
        purged = 0

        for pump in pumps:
            # Only purge pumps with assigned liquids
            if pump.get('liquid_id'):
                try:
                    arduino_service.start_pump(pump['id'])
                    purged += 1
                    # Small delay between pumps
                    import time
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Failed to purge pump {pump['id']}: {e}")

        return ApiResponse(
            success=True,
            message=f"Purged {purged} pumps for {request.duration_seconds} seconds each"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to purge all pumps: {str(e)}"
        )
