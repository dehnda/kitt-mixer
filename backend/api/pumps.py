from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional, Union
from models import Pump, PumpUpdate, ApiResponse
from pydantic import BaseModel

router = APIRouter(prefix="/pumps", tags=["Pumps"])


class PumpConfigUpdate(BaseModel):
    """Update pump configuration"""
    liquid_id: Union[int, None] = None
    ml_per_second: Optional[float] = None


class PumpTestRequest(BaseModel):
    """Request to test pump"""
    duration_seconds: float = 10.0
    reverse: bool = False  # Run pump in reverse (for priming/clearing)


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

    # Update pump configuration - check if fields were provided
    success = True
    liquid_name = None
    
    # Check if liquid_id was provided (even if None/null)
    if update.model_fields_set and 'liquid_id' in update.model_fields_set:
        success = db_service.update_pump_liquid(pump_id, update.liquid_id)
        if update.liquid_id:
            liquid_name = db_service.get_liquid_by_id(update.liquid_id)
    
    # Check if ml_per_second was provided
    if success and update.model_fields_set and 'ml_per_second' in update.model_fields_set:
        success = db_service.update_pump_flow_rate(pump_id, update.ml_per_second)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update pump configuration"
        )

    message = f"Pump {pump_id}"
    if liquid_name:
        message += f" ({liquid_name})"
    message += " updated successfully"
    
    return ApiResponse(
        success=True,
        message=message
    )


@router.post("/{pump_id}/test", response_model=ApiResponse)
async def test_pump(pump_id: int, request: PumpTestRequest, db_service, gpio_controller):
    """Test pump for calibration (run for specified duration)"""
    # Verify pump exists
    pump = db_service.get_pump_by_id(pump_id)    
    if not pump:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pump {pump_id} not found"
        )
    
    if not gpio_controller.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GPIO Controller not connected"
        )
    
    try:
        # Calculate duration in ms
        duration_ms = int(request.duration_seconds * 1000)
        
        # Start pump (with reverse if requested)
        success = gpio_controller.start_pump(pump_id, duration_ms, reverse=request.reverse)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to start pump {pump_id}"
            )

        mode = "REVERSE" if request.reverse else "FORWARD"
        return ApiResponse(
            success=True,
            message=f"Pump {pump_id} started in {mode} mode for {request.duration_seconds} seconds",
            data={"pump_id": pump_id, "duration": request.duration_seconds, "reverse": request.reverse}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start pump: {str(e)}"
        )


@router.post("/{pump_id}/stop", response_model=ApiResponse)
async def stop_pump(pump_id: int, db_service, gpio_controller):
    """Stop a pump immediately"""
    # Verify pump exists
    pump = db_service.get_pump_by_id(pump_id)
    if not pump:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pump {pump_id} not found"
        )

    if not gpio_controller.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GPIO Controller not connected"
        )

    try:
        # Stop pump
        success = gpio_controller.stop_pump(pump_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to stop pump {pump_id}"
            )

        return ApiResponse(
            success=True,
            message=f"Pump {pump_id} stopped",
            data={"pump_id": pump_id}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop pump: {str(e)}"
        )


@router.post("/stop-all", response_model=ApiResponse)
async def stop_all_pumps(gpio_controller):
    """Stop all pumps immediately"""
    if not gpio_controller.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GPIO Controller not connected"
        )

    try:
        # Stop all pumps
        success = gpio_controller.stop_all_pumps()
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to stop all pumps"
            )

        return ApiResponse(
            success=True,
            message="All pumps stopped"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop pumps: {str(e)}"
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
async def test_all_pumps(request: PumpTestRequest, db_service, gpio_controller):
    """Test all pumps sequentially"""
    if not gpio_controller.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GPIO Controller not connected"
        )

    try:
        pumps = db_service.get_all_pumps()
        tested = 0
        duration_ms = int(request.duration_seconds * 1000)

        for pump in pumps:
            try:
                gpio_controller.start_pump(pump['id'], duration_ms)
                tested += 1
                # Wait for pump to finish plus small delay
                import time
                time.sleep(request.duration_seconds + 0.5)
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
async def purge_all_pumps(request: PumpTestRequest, db_service, gpio_controller):
    """Purge all pumps with assigned liquids to clear lines"""
    if not gpio_controller.is_connected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GPIO Controller not connected"
        )

    try:
        pumps = db_service.get_all_pumps()
        purged = 0
        duration_ms = int(request.duration_seconds * 1000)

        for pump in pumps:
            # Only purge pumps with assigned liquids
            if pump.get('liquid_id'):
                try:
                    gpio_controller.start_pump(pump['id'], duration_ms)
                    purged += 1
                    # Wait for pump to finish plus small delay
                    import time
                    time.sleep(request.duration_seconds + 0.5)
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
