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
        self.auto_reconnect = True
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3

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
            self.reconnect_attempts = 0  # Reset counter on successful connection
            print(f"Connected to Arduino on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")
            self.is_connected = False
            return False

    def try_reconnect(self) -> bool:
        """Attempt to reconnect to Arduino"""
        if not self.auto_reconnect:
            return False

        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print(f"Max reconnect attempts ({self.max_reconnect_attempts}) reached")
            return False

        self.reconnect_attempts += 1
        print(f"Attempting to reconnect to Arduino (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})...")

        # Close existing connection if any
        if self.serial_connection:
            try:
                self.serial_connection.close()
            except:
                pass

        time.sleep(1)  # Wait before reconnecting
        return self.connect()

    def disconnect(self):
        """Close serial connection"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            print("Disconnected from Arduino")

    def send_command(self, command: str) -> Optional[str]:
        """Send a command to Arduino and return response"""
        if not self.is_connected or not self.serial_connection:
            # Try to reconnect if enabled
            if self.auto_reconnect and self.try_reconnect():
                # Reconnection successful, proceed with command
                pass
            else:
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

                # Try to reconnect
                if self.auto_reconnect and self.try_reconnect():
                    # Retry the command once after reconnection
                    try:
                        self.serial_connection.reset_input_buffer()
                        cmd = f"{command}\n"
                        self.serial_connection.write(cmd.encode())
                        response = self.serial_connection.readline().decode().strip()
                        return response
                    except:
                        return None

                return None

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

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
