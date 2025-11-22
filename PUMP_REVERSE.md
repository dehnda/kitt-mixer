# Pump Reverse Control

## Overview
GPIO pin 23 controls the reverse direction for all pumps. This is useful for:
- **Priming pumps** - Fill lines with liquid
- **Cleaning lines** - Push liquid back to clear tubes
- **Maintenance** - Remove air bubbles or blockages

## Hardware Connection
- **Pin 23 (BCM numbering)** - Pump reverse control (shared by all 8 pumps)
- **LOW (0V)** - Forward direction (normal operation)
- **HIGH (3.3V)** - Reverse direction (for priming/cleaning)

## GPIO Controller Changes

### Configuration Constants
```python
PUMP_REVERSE_PIN = 23  # GPIO pin for pump reverse control
```

### New Methods

#### `start_pump(pump_id, duration_ms, reverse=False)`
Updated to support reverse parameter:
```python
# Normal forward operation
gpio_controller.start_pump(pump_id=1, duration_ms=5000)

# Reverse operation for priming
gpio_controller.start_pump(pump_id=1, duration_ms=5000, reverse=True)
```

#### `set_pump_reverse(enabled)`
Manually control reverse pin for all pumps:
```python
# Enable reverse mode
gpio_controller.set_pump_reverse(True)

# Disable reverse mode (forward)
gpio_controller.set_pump_reverse(False)
```

#### `prime_pump(pump_id, duration_ms=3000, reverse=False)`
Convenience method for priming/cleaning:
```python
# Prime pump forward (fill line)
gpio_controller.prime_pump(pump_id=1, duration_ms=3000)

# Reverse prime (clear line)
gpio_controller.prime_pump(pump_id=1, duration_ms=3000, reverse=True)
```

## Status Information

The `get_status()` method now includes:
```json
{
  "connected": true,
  "pump_reverse_enabled": false,
  "pump_reverse_pin": 23,
  "pumps": { ... },
  "mixer": { ... }
}
```

## Usage Examples

### Example 1: Prime a pump before mixing
```python
# Prime pump 1 with 3 seconds forward
gpio_controller.prime_pump(pump_id=1, duration_ms=3000, reverse=False)
```

### Example 2: Clear a line after mixing
```python
# Run pump 2 in reverse for 2 seconds to clear line
gpio_controller.prime_pump(pump_id=2, duration_ms=2000, reverse=True)
```

### Example 3: Normal cocktail mixing (forward only)
```python
# Mix ingredients normally (reverse=False is default)
gpio_controller.start_pump(pump_id=1, duration_ms=5000)
gpio_controller.start_pump(pump_id=3, duration_ms=3000)
```

## Safety Notes

1. **Direction changes**: The reverse pin affects ALL pumps simultaneously
2. **Don't run pumps dry**: Always ensure there's liquid to pump
3. **Check connections**: Verify reverse wiring is correct before use
4. **Test first**: Always test priming on a single pump before mixing

## Pin Summary

| GPIO Pin | Function | Default State |
|----------|----------|---------------|
| 2-6, 9-11 | Pump control (1-8) | LOW (off) |
| 23 | Pump reverse | LOW (forward) |
| 16 | Stepper STEP | LOW |
| 12 | Stepper DIR | LOW |
| 26 | Stepper ENABLE | HIGH (disabled) |

## Future Enhancements

Potential additions:
- API endpoints for priming/cleaning
- Frontend UI for maintenance mode
- Automatic line purging after mixing
- Individual pump reverse control (if hardware supports)
