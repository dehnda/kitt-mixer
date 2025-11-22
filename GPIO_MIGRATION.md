# GPIO Migration Complete

## Summary
The backend has been successfully migrated from Arduino serial communication to direct Raspberry Pi GPIO control.

## Changes Made

### 1. **main.py** - Application Entry Point
- Replaced `ArduinoService` with `GPIOController`
- Updated dependency injection to use `get_gpio_controller()`
- Health check now reports `gpio_connected` instead of `arduino_connected`
- On shutdown, properly disconnects GPIO and stops all pumps/mixer

### 2. **services/gpio_controller.py** - GPIO Hardware Control
- Added mock GPIO support for development on non-Raspberry Pi systems
- Controls 8 pumps directly via GPIO pins 18-25 (BCM mode)
- Controls stepper motor mixer via GPIO pins:
  - Step Pin: 16
  - Direction Pin: 12
  - Enable Pin: 26
- Features:
  - Timed pump operation with automatic shutoff
  - Stepper motor control with configurable duration and direction
  - Thread-safe operation with locks
  - Mock mode for development/testing

### 3. **services/mixer.py** - Cocktail Mixing Logic
- Removed `ArduinoService` dependency
- Now exclusively uses `GPIOController`
- Automatically starts mixer motor for 10 seconds after dispensing cocktail
- Emergency stop now stops both pumps AND mixer motor
- Cancel operation stops both pumps AND mixer motor

### 4. **api/pumps.py** - Pump Control Endpoints
- Updated all endpoints to use `gpio_controller` instead of `arduino_service`
- Test pump endpoint now calculates duration in milliseconds
- Test-all and purge-all endpoints now properly wait for pump operations to complete
- Error messages updated to reference "GPIO Controller" instead of "Arduino"

### 5. **api/status.py** - Status & Diagnostics
- Updated status endpoint to report `gpio_connected`
- Diagnostics now check GPIO instead of Arduino
- Added new mixer motor control endpoints:
  - `POST /api/v1/status/mixer/start` - Start mixer motor
  - `POST /api/v1/status/mixer/stop` - Stop mixer motor
  - `GET /api/v1/status/mixer` - Get mixer motor status

## GPIO Pin Assignments

### Pumps (BCM Numbering)
- Pump 1: GPIO 18
- Pump 2: GPIO 19
- Pump 3: GPIO 20
- Pump 4: GPIO 21
- Pump 5: GPIO 22
- Pump 6: GPIO 23
- Pump 7: GPIO 24
- Pump 8: GPIO 25

### Stepper Motor (Mixer)
- Step Pin: GPIO 16
- Direction Pin: GPIO 12
- Enable Pin: GPIO 26

## Development vs Production

### Development Mode (Non-Raspberry Pi)
- Mock GPIO is automatically used
- All operations are simulated with console logging
- No real hardware interaction
- Perfect for testing API logic and frontend

### Production Mode (Raspberry Pi)
- Real RPi.GPIO library is used
- Direct hardware control via GPIO pins
- Pump timing based on `ml_per_second` flow rate
- Stepper motor runs at configured RPM (default: 60 RPM, 200 steps/revolution)

## API Changes

### Removed
- No Arduino serial port configuration needed
- No Arduino connection settings in database

### New Endpoints
```
POST /api/v1/status/mixer/start
POST /api/v1/status/mixer/stop
GET /api/v1/status/mixer
```

### Modified Endpoints
- All pump endpoints now use GPIO directly
- Status endpoint reports GPIO connection status
- Diagnostics endpoint reports GPIO status

## Hardware Setup

### Pump Connections
Connect 8 pumps (relays) to the following GPIO pins:
- Each pump should be connected to a relay module
- Relay modules trigger on HIGH signal
- Common ground between Pi and relay module

### Stepper Motor Connection
Connect stepper motor driver (e.g., A4988, DRV8825) to:
- STEP → GPIO 16
- DIR → GPIO 12
- ENABLE → GPIO 26
- Also connect motor power, ground, and motor coils per driver specs

## Testing

### Test Individual Pump
```bash
curl -X POST http://localhost:8000/api/v1/pumps/1/test \
  -H "Content-Type: application/json" \
  -d '{"duration_seconds": 5.0}'
```

### Test Mixer Motor
```bash
# Start mixer for 10 seconds
curl -X POST http://localhost:8000/api/v1/status/mixer/start \
  -H "Content-Type: application/json" \
  -d '{"duration_seconds": 10.0, "clockwise": true}'

# Stop mixer
curl -X POST http://localhost:8000/api/v1/status/mixer/stop
```

### Check Status
```bash
curl http://localhost:8000/api/v1/status
```

## Next Steps

1. ✅ Backend migration complete
2. Test on Raspberry Pi with real hardware
3. Calibrate pump flow rates (`ml_per_second`)
4. Adjust stepper motor speed if needed (in `gpio_controller.py`)
5. Optional: Update frontend to show mixer motor controls
6. Optional: Remove Arduino files if no longer needed

## Troubleshooting

### "GPIO Controller not connected"
- On Raspberry Pi: Check that user has GPIO permissions (usually needs to be in `gpio` group)
- Not on Raspberry Pi: This is expected, system runs in mock mode

### Pumps not working
- Check GPIO pin connections (BCM numbering, not physical pin numbers)
- Verify relay module is powered correctly
- Test with simple LED first to verify GPIO control

### Stepper motor not working
- Check driver is powered
- Verify ENABLE pin logic (LOW = enabled)
- Check motor power supply
- Verify step/dir connections

## Files Modified

- `backend/main.py`
- `backend/services/mixer.py`
- `backend/services/gpio_controller.py`
- `backend/api/pumps.py`
- `backend/api/status.py`

## Files Unchanged (Can be removed if desired)

- `backend/services/arduino.py` - Old serial communication service
- `arduino/pump_controller/pump_controller.ino` - Arduino sketch
