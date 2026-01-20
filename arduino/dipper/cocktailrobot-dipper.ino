// Include libraries
#include <Stepper.h>
#include <Adafruit_NeoPixel.h>
#include "MixerArm.h"
#include "LedControl.h"

// Number of steps per internal motor revolution
const float STEPS_PER_REV = 32;

//  Amount of Gear Reduction
const float GEAR_RED = 64;

// Number of steps per geared output rotation
const float STEPS_PER_OUT_REV = STEPS_PER_REV * GEAR_RED;

// Motor pins
const int PIN_1IN = 12;
const int PIN_2IN = 11;
const int PIN_3IN = 10;
const int PIN_4IN = 9;

// Endstop pins
const int PIN_LOWER_ENDSTOP = 2;
const int PIN_UPPER_ENDSTOP = 3;

const int PIN_MIXER_MOTOR = 5;

// LED pins and settings
const int LED_PIN = 7;
const int NUM_PIXELS = 25;
const int LED_BRIGHTNESS = 100;

// Create instances
MixerArm mixerArm(
  1000, STEPS_PER_REV, PIN_LOWER_ENDSTOP, PIN_UPPER_ENDSTOP,
  PIN_1IN, PIN_3IN, PIN_2IN, PIN_4IN, PIN_MIXER_MOTOR);

LedControl ledControl(LED_PIN, NUM_PIXELS, LED_BRIGHTNESS);

void setup() {
  // Initialize serial communication for debugging
  Serial.begin(9600);
  Serial.println("K.I.T.T. Mixer Arm online.");

  mixerArm.setup();
  ledControl.setup();

  // Start with idle LED pattern
  ledControl.setIdling();
}

void loop() {
  static bool hasError = false;

  // Handle serial commands for LED control
  if (Serial.available()) {
    char cmd = Serial.read();

    switch (cmd) {
      case '1':
        Serial.println("Wait for pump");
        mixerArm.waitForPump();
        break;

      case '2':
        Serial.println("Start mixing");
        mixerArm.startSequence();
        break;

      case '3':
        Serial.println("Abort mixing");
        mixerArm.stopSequence();
        break;

      case '4':
        Serial.println("Start mixer motor");
        digitalWrite(PIN_MIXER_MOTOR, HIGH);
        break;

      case '5':
        Serial.println("Stop mixer motor");
        digitalWrite(PIN_MIXER_MOTOR, LOW);
        break;

      case '6':
        Serial.println("Status Report:");
        Serial.println("   Endstop1: " + digitalRead(PIN_LOWER_ENDSTOP) == LOW ? "LOW" : "HIGH");
        Serial.println("   Endstop2: " + digitalRead(PIN_UPPER_ENDSTOP) == LOW ? "LOW" : "HIGH");
        break;

      case '8':
        Serial.println("Set to error state");
        hasError = true;
        break;
        
      case '9':
        Serial.println("Reset error state");
        hasError = false;
        break;
    }
  }

  if (mixerArm.isRunning()) {
    ledControl.setWorking();
  } else if (!mixerArm.isRunning() && mixerArm.getArmState() != MixerArm::ArmState::armIsUp) {
    ledControl.setWorking();
  } else if (hasError) {
    ledControl.setError();
  } else {
    ledControl.setIdling();
  }

  mixerArm.loop();
  ledControl.loop();
}
