try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except (ImportError, RuntimeError):
    # Running on non-Raspberry Pi or GPIO not available
    HAS_GPIO = False
    print("RPi.GPIO not available - running in mock mode")
    
    # Mock GPIO class for development
    class MockGPIO:
        BCM = "BCM"
        OUT = "OUT"
        HIGH = 1
        LOW = 0
        
        @staticmethod
        def setmode(mode):
            pass
        
        @staticmethod
        def setwarnings(flag):
            pass
        
        @staticmethod
        def setup(pin, mode):
            pass
        
        @staticmethod
        def output(pin, state):
            pass
        
        @staticmethod
        def cleanup():
            pass
    
    GPIO = MockGPIO()

import time
from typing import Optional, Dict, List
import threading
from dataclasses import dataclass
from enum import Enum


# ============================================================================
# GPIO PIN CONFIGURATION - Change these values to match your wiring
# ============================================================================

# Pump GPIO pins (BCM numbering)
PUMP_1_PIN = 6
PUMP_2_PIN = 5
PUMP_3_PIN = 11
PUMP_4_PIN = 9
PUMP_5_PIN = 10
PUMP_6_PIN = 4
PUMP_7_PIN = 3
PUMP_8_PIN = 2

# Pump reverse control pin (shared for all pumps)
PUMP_REVERSE_PIN = 23

# Stepper motor GPIO pins (BCM numbering)
STEPPER_STEP_PIN = 16
STEPPER_DIR_PIN = 12
STEPPER_ENABLE_PIN = 26

# Stepper motor parameters
STEPPER_STEPS_PER_REV = 200  # Standard 1.8° stepper motor
STEPPER_RPM = 60             # Rotation speed

# Default pump flow rates (ml per second)
DEFAULT_FLOW_RATE = 1.0

# Pump control logic (set to False if your relays are active-LOW)
# True = GPIO.HIGH turns pump ON, GPIO.LOW turns pump OFF (active-HIGH)
# False = GPIO.LOW turns pump ON, GPIO.HIGH turns pump OFF (active-LOW)
PUMP_ACTIVE_HIGH = False  # Most relay boards are active-LOW

# ============================================================================


class StepperDirection(Enum):
    CLOCKWISE = 1
    COUNTERCLOCKWISE = -1


@dataclass
class PumpConfig:
    """Configuration for a pump"""
    gpio_pin: int
    ml_per_second: float = 1.0  # Default flow rate
    name: str = ""


@dataclass 
class StepperConfig:
    """Configuration for stepper motor"""
    step_pin: int
    dir_pin: int
    enable_pin: int
    steps_per_revolution: int = 200
    rpm: int = 60


class GPIOController:
    """Service for controlling pumps and stepper motor via Raspberry Pi GPIO"""

    def __init__(self):
        # GPIO pin configurations
        self.pump_configs = {
            1: PumpConfig(gpio_pin=PUMP_1_PIN, ml_per_second=DEFAULT_FLOW_RATE, name="Pump 1"),
            2: PumpConfig(gpio_pin=PUMP_2_PIN, ml_per_second=DEFAULT_FLOW_RATE, name="Pump 2"),
            3: PumpConfig(gpio_pin=PUMP_3_PIN, ml_per_second=DEFAULT_FLOW_RATE, name="Pump 3"),
            4: PumpConfig(gpio_pin=PUMP_4_PIN, ml_per_second=DEFAULT_FLOW_RATE, name="Pump 4"),
            5: PumpConfig(gpio_pin=PUMP_5_PIN, ml_per_second=DEFAULT_FLOW_RATE, name="Pump 5"),
            6: PumpConfig(gpio_pin=PUMP_6_PIN, ml_per_second=DEFAULT_FLOW_RATE, name="Pump 6"),
            7: PumpConfig(gpio_pin=PUMP_7_PIN, ml_per_second=DEFAULT_FLOW_RATE, name="Pump 7"),
            8: PumpConfig(gpio_pin=PUMP_8_PIN, ml_per_second=DEFAULT_FLOW_RATE, name="Pump 8"),
        }
        
        # Pump reverse control pin
        self.pump_reverse_pin = PUMP_REVERSE_PIN
        
        # Stepper motor configuration (for mixer unit)
        self.stepper_config = StepperConfig(
            step_pin=STEPPER_STEP_PIN,
            dir_pin=STEPPER_DIR_PIN,
            enable_pin=STEPPER_ENABLE_PIN,
            steps_per_revolution=STEPPER_STEPS_PER_REV,
            rpm=STEPPER_RPM
        )
        
        self.is_connected = False
        self.lock = threading.Lock()
        
        # Pump state tracking
        self.pump_timers: Dict[int, threading.Timer] = {}
        self.pump_states: Dict[int, bool] = {}
        self.pump_reverse_enabled = False  # Track reverse state
        
        # Stepper state
        self.stepper_running = False
        self.stepper_thread: Optional[threading.Thread] = None

    def connect(self) -> bool:
        """Initialize GPIO pins"""
        if not HAS_GPIO:
            print("GPIO Controller running in MOCK MODE (development)")
            self.is_connected = True
            # Initialize mock pump states
            for pump_id in self.pump_configs.keys():
                self.pump_states[pump_id] = False
            return True
            
        try:
            # Set GPIO mode
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup pump pins as outputs
            for pump_id, config in self.pump_configs.items():
                GPIO.setup(config.gpio_pin, GPIO.OUT)
                GPIO.output(config.gpio_pin, GPIO.HIGH)  # Pumps off by default
                self.pump_states[pump_id] = False
            
            # Setup pump reverse control pin
            GPIO.setup(self.pump_reverse_pin, GPIO.OUT)
            GPIO.output(self.pump_reverse_pin, GPIO.LOW)  # Forward direction by default
            self.pump_reverse_enabled = False
            
            # Setup stepper motor pins
            GPIO.setup(self.stepper_config.step_pin, GPIO.OUT)
            GPIO.setup(self.stepper_config.dir_pin, GPIO.OUT)
            GPIO.setup(self.stepper_config.enable_pin, GPIO.OUT)
            
            # Disable stepper motor by default
            GPIO.output(self.stepper_config.enable_pin, GPIO.HIGH)
            
            self.is_connected = True
            print("GPIO Controller initialized successfully")
            return True
            
        except Exception as e:
            print(f"Failed to initialize GPIO: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """Clean up GPIO"""
        try:
            # Stop all pumps
            self.stop_all_pumps()
            
            # Stop stepper motor
            self.stop_mixer()
            
            # Clean up GPIO
            GPIO.cleanup()
            self.is_connected = False
            print("GPIO Controller disconnected")
        except Exception as e:
            print(f"Error during GPIO cleanup: {e}")

    def start_pump(self, pump_id: int, duration_ms: int, reverse: bool = False) -> bool:
        """
        Start a pump for specified duration

        Args:
            pump_id: ID of the pump to activate (1-8)
            duration_ms: Duration in milliseconds
            reverse: If True, run pump in reverse (for priming/cleaning)

        Returns:
            True if command successful, False otherwise
        """
        if not self.is_connected:
            print("GPIO Controller not connected")
            return False
            
        if pump_id not in self.pump_configs:
            print(f"Invalid pump ID: {pump_id}")
            return False

        with self.lock:
            try:
                config = self.pump_configs[pump_id]
                
                # Cancel existing timer if any
                if pump_id in self.pump_timers:
                    self.pump_timers[pump_id].cancel()
                
                # Set reverse direction if needed
                if reverse:
                    GPIO.output(self.pump_reverse_pin, GPIO.HIGH)
                    self.pump_reverse_enabled = True
                else:
                    GPIO.output(self.pump_reverse_pin, GPIO.LOW)
                    self.pump_reverse_enabled = False
                
                # Turn on pump (respect active logic setting)
                pump_on_state = GPIO.HIGH if PUMP_ACTIVE_HIGH else GPIO.LOW
                GPIO.output(config.gpio_pin, pump_on_state)
                self.pump_states[pump_id] = True
                
                # Set timer to turn off pump
                timer = threading.Timer(duration_ms / 1000.0, self._stop_pump_callback, [pump_id])
                self.pump_timers[pump_id] = timer
                timer.start()
                
                direction_str = "reverse" if reverse else "forward"
                print(f"Pump {pump_id} ({config.name}) started for {duration_ms}ms ({direction_str})")
                return True
                
            except Exception as e:
                print(f"Error starting pump {pump_id}: {e}")
                return False

    def _stop_pump_callback(self, pump_id: int):
        """Callback to stop pump when timer expires"""
        try:
            config = self.pump_configs[pump_id]
            # Turn off pump (respect active logic setting)
            pump_off_state = GPIO.LOW if PUMP_ACTIVE_HIGH else GPIO.HIGH
            GPIO.output(config.gpio_pin, pump_off_state)
            self.pump_states[pump_id] = False
            print(f"Pump {pump_id} ({config.name}) stopped automatically")
        except Exception as e:
            print(f"Error in pump stop callback: {e}")

    def stop_pump(self, pump_id: int) -> bool:
        """
        Stop a pump immediately

        Args:
            pump_id: ID of the pump to stop

        Returns:
            True if command successful, False otherwise
        """
        if not self.is_connected:
            print("GPIO Controller not connected")
            return False
            
        if pump_id not in self.pump_configs:
            print(f"Invalid pump ID: {pump_id}")
            return False

        with self.lock:
            try:
                config = self.pump_configs[pump_id]
                
                # Cancel timer if any
                if pump_id in self.pump_timers:
                    self.pump_timers[pump_id].cancel()
                    del self.pump_timers[pump_id]
                
                # Turn off pump (respect active logic setting)
                pump_off_state = GPIO.LOW if PUMP_ACTIVE_HIGH else GPIO.HIGH
                GPIO.output(config.gpio_pin, pump_off_state)
                self.pump_states[pump_id] = False
                
                print(f"Pump {pump_id} ({config.name}) stopped")
                return True
                
            except Exception as e:
                print(f"Error stopping pump {pump_id}: {e}")
                return False

    def stop_all_pumps(self) -> bool:
        """Stop all pumps immediately"""
        if not self.is_connected:
            print("GPIO Controller not connected")
            return False

        with self.lock:
            try:
                # Cancel all timers
                for timer in self.pump_timers.values():
                    timer.cancel()
                self.pump_timers.clear()
                
                # Turn off all pumps (respect active logic setting)
                pump_off_state = GPIO.LOW if PUMP_ACTIVE_HIGH else GPIO.HIGH
                for pump_id, config in self.pump_configs.items():
                    GPIO.output(config.gpio_pin, pump_off_state)
                    self.pump_states[pump_id] = False
                
                print("All pumps stopped")
                return True
                
            except Exception as e:
                print(f"Error stopping all pumps: {e}")
                return False

    def set_pump_reverse(self, enabled: bool) -> bool:
        """
        Enable or disable reverse mode for all pumps
        
        Args:
            enabled: True to enable reverse, False for forward
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            print("GPIO Controller not connected")
            return False
            
        try:
            GPIO.output(self.pump_reverse_pin, GPIO.HIGH if enabled else GPIO.LOW)
            self.pump_reverse_enabled = enabled
            direction = "reverse" if enabled else "forward"
            print(f"Pump direction set to {direction}")
            return True
        except Exception as e:
            print(f"Error setting pump reverse: {e}")
            return False

    def prime_pump(self, pump_id: int, duration_ms: int = 3000, reverse: bool = False) -> bool:
        """
        Prime a pump (convenience method for maintenance/testing)
        
        Args:
            pump_id: ID of the pump to prime (1-8)
            duration_ms: Duration in milliseconds (default 3 seconds)
            reverse: If True, run in reverse to clear lines
            
        Returns:
            True if successful, False otherwise
        """
        return self.start_pump(pump_id, duration_ms, reverse=reverse)

    def start_mixer(self, duration_seconds: Optional[float] = None, direction: StepperDirection = StepperDirection.CLOCKWISE) -> bool:
        """
        Start the mixer (stepper motor)

        Args:
            duration_seconds: How long to run mixer (None for continuous)
            direction: Direction to rotate

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            print("GPIO Controller not connected")
            return False

        if self.stepper_running:
            print("Mixer already running")
            return True

        try:
            self.stepper_running = True
            
            # Set direction
            GPIO.output(self.stepper_config.dir_pin, 
                       GPIO.HIGH if direction == StepperDirection.CLOCKWISE else GPIO.LOW)
            
            # Enable stepper motor
            GPIO.output(self.stepper_config.enable_pin, GPIO.LOW)
            
            # Start stepper in separate thread
            self.stepper_thread = threading.Thread(
                target=self._run_stepper, 
                args=(duration_seconds,)
            )
            self.stepper_thread.start()
            
            print(f"Mixer started ({'continuous' if duration_seconds is None else f'{duration_seconds}s'})")
            return True
            
        except Exception as e:
            print(f"Error starting mixer: {e}")
            self.stepper_running = False
            return False

    def _run_stepper(self, duration_seconds: Optional[float]):
        """Run stepper motor in separate thread"""
        try:
            # Calculate step delay from RPM
            steps_per_second = (self.stepper_config.rpm * self.stepper_config.steps_per_revolution) / 60
            step_delay = 1.0 / (2 * steps_per_second)  # Half period for high/low
            
            start_time = time.time()
            
            while self.stepper_running:
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    break
                    
                # Step pulse
                GPIO.output(self.stepper_config.step_pin, GPIO.HIGH)
                time.sleep(step_delay)
                GPIO.output(self.stepper_config.step_pin, GPIO.LOW)
                time.sleep(step_delay)
                
        except Exception as e:
            print(f"Error in stepper thread: {e}")
        finally:
            # Disable stepper motor
            GPIO.output(self.stepper_config.enable_pin, GPIO.HIGH)
            self.stepper_running = False
            print("Mixer stopped")

    def stop_mixer(self) -> bool:
        """Stop the mixer"""
        if not self.stepper_running:
            return True
            
        try:
            self.stepper_running = False
            
            if self.stepper_thread and self.stepper_thread.is_alive():
                self.stepper_thread.join(timeout=1.0)
            
            # Disable stepper motor
            GPIO.output(self.stepper_config.enable_pin, GPIO.HIGH)
            
            print("Mixer stopped")
            return True
            
        except Exception as e:
            print(f"Error stopping mixer: {e}")
            return False

    def get_status(self) -> Dict:
        """Get current GPIO controller status"""
        return {
            "connected": self.is_connected,
            "pump_reverse_enabled": self.pump_reverse_enabled,
            "pump_reverse_pin": self.pump_reverse_pin,
            "pumps": {
                pump_id: {
                    "active": self.pump_states.get(pump_id, False),
                    "name": config.name,
                    "gpio_pin": config.gpio_pin
                }
                for pump_id, config in self.pump_configs.items()
            },
            "mixer": {
                "running": self.stepper_running,
                "step_pin": self.stepper_config.step_pin,
                "dir_pin": self.stepper_config.dir_pin,
                "enable_pin": self.stepper_config.enable_pin
            }
        }

    def calculate_duration_ms(self, ml: float, pump_id: int) -> int:
        """
        Calculate pump duration in milliseconds based on volume

        Args:
            ml: Volume to dispense in milliliters
            pump_id: ID of the pump (for flow rate lookup)

        Returns:
            Duration in milliseconds
        """
        if pump_id in self.pump_configs:
            ml_per_second = self.pump_configs[pump_id].ml_per_second
            seconds = ml / ml_per_second
            return int(seconds * 1000)
        else:
            # Default flow rate
            return int(ml * 1000)  # 1 ml/s default

    def set_pump_flow_rate(self, pump_id: int, ml_per_second: float) -> bool:
        """Set flow rate for a specific pump"""
        if pump_id in self.pump_configs:
            self.pump_configs[pump_id].ml_per_second = ml_per_second
            print(f"Set pump {pump_id} flow rate to {ml_per_second} ml/s")
            return True
        return False

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
