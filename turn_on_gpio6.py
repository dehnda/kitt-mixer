#!/usr/bin/env python3
"""
Script to turn on GPIO pin on Raspberry Pi 4B
"""

import RPi.GPIO as GPIO
import time
import argparse

def setup_gpio(gpio_pin):
    """Initialize GPIO settings"""
    # Use BCM pin numbering
    GPIO.setmode(GPIO.BCM)
    
    # Set GPIO pin as output
    GPIO.setup(gpio_pin, GPIO.OUT)
    
    print(f"GPIO pin {gpio_pin} set up as output")

def turn_on_gpio(gpio_pin):
    """Turn on the GPIO pin"""
    GPIO.output(gpio_pin, GPIO.HIGH)
    print(f"GPIO pin {gpio_pin} is now ON (HIGH)")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Turn on a GPIO pin on Raspberry Pi 4B')
    parser.add_argument('pin', type=int, nargs='?', default=6,
                        help='GPIO pin number (BCM numbering), default is 6')
    args = parser.parse_args()
    
    gpio_pin = args.pin
    
    try:
        setup_gpio(gpio_pin)
        turn_on_gpio(gpio_pin)
        
        # Keep the pin on
        print("Press Ctrl+C to turn off and exit")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Clean up GPIO on exit
        GPIO.cleanup()
        print(f"GPIO pin {gpio_pin} cleaned up")

if __name__ == "__main__":
    main()
