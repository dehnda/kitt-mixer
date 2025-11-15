import serial
import time
from typing import Optional
import threading


class ArduinoService:
    """Service for communicating with Arduino via serial connection"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: int = 2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection: Optional[serial.Serial] = None
        self.is_connected = False
        self.lock = threading.Lock()
    
    def connect(self) -> bool:
        """Establish serial connection to Arduino"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # Wait for Arduino to reset after connection
            self.is_connected = True
            print(f"Connected to Arduino on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            print("Disconnected from Arduino")
    
    def send_command(self, command: str) -> Optional[str]:
        """Send a command to Arduino and return response"""
        if not self.is_connected or not self.serial_connection:
            print("Arduino not connected")
            return None
        
        with self.lock:
            try:
                # Clear input buffer
                self.serial_connection.reset_input_buffer()
                
                # Send command
                cmd = f"{command}\n"
                self.serial_connection.write(cmd.encode())
                
                # Read response
                response = self.serial_connection.readline().decode().strip()
                return response
            except serial.SerialException as e:
                print(f"Serial communication error: {e}")
                self.is_connected = False
                return None
    
    def start_pump(self, pump_id: int, duration_ms: int) -> bool:
        """
        Start a pump for specified duration
        
        Args:
            pump_id: ID of the pump to activate
            duration_ms: Duration in milliseconds
        
        Returns:
            True if command successful, False otherwise
        """
        command = f"START:{pump_id},{duration_ms}"
        response = self.send_command(command)
        
        if response and response.startswith("OK"):
            print(f"Pump {pump_id} started for {duration_ms}ms")
            return True
        else:
            print(f"Failed to start pump {pump_id}: {response}")
            return False
    
    def stop_pump(self, pump_id: int) -> bool:
        """
        Stop a pump immediately
        
        Args:
            pump_id: ID of the pump to stop
        
        Returns:
            True if command successful, False otherwise
        """
        command = f"STOP:{pump_id}"
        response = self.send_command(command)
        
        if response and response.startswith("OK"):
            print(f"Pump {pump_id} stopped")
            return True
        else:
            print(f"Failed to stop pump {pump_id}: {response}")
            return False
    
    def stop_all_pumps(self) -> bool:
        """Stop all pumps immediately"""
        command = "STOP:ALL"
        response = self.send_command(command)
        
        if response and response.startswith("OK"):
            print("All pumps stopped")
            return True
        else:
            print(f"Failed to stop all pumps: {response}")
            return False
    
    def get_status(self) -> Optional[str]:
        """Get current Arduino status"""
        command = "STATUS"
        response = self.send_command(command)
        
        if response and response.startswith("STATUS:"):
            status = response.split(":", 1)[1]
            return status
        else:
            print(f"Failed to get status: {response}")
            return None
    
    def calculate_duration_ms(self, ml: float, ml_per_second: float) -> int:
        """
        Calculate pump duration in milliseconds based on volume
        
        Args:
            ml: Volume to dispense in milliliters
            ml_per_second: Pump flow rate
        
        Returns:
            Duration in milliseconds
        """
        seconds = ml / ml_per_second
        return int(seconds * 1000)
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
