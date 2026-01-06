#include "Arduino.h"
#include <Stepper.h>
#include "MixerArm.h"

MixerArm::MixerArm(
  int speed,
  float steps_per_revolution,
  int pin_lowerEndstop,
  int pin_upperEndstop,
  int pin_1in,
  int pin_3in,
  int pin_2in,
  int pin_4in,
  int pin_mixer)

  // Create Instance of Stepper Class
  // Specify Pins used for motor coils
  // Connected to ULN2003 Motor Driver In1, In2, In3, In4
  // Pins entered in sequence 1-3-2-4 for proper step sequencing
  : _steppermotor(steps_per_revolution, pin_1in, pin_3in, pin_2in, pin_4in) {
  _speed = speed;
  _armState = armIsUnknown;
  _running = false;
  _pin_lowerEndstop = pin_lowerEndstop;
  _pin_upperEndstop = pin_upperEndstop;
  _pin_1in = pin_1in;
  _pin_2in = pin_2in;
  _pin_3in = pin_3in;
  _pin_4in = pin_4in;
  _pin_mixer = pin_mixer;
}

void MixerArm::setup() {
  pinMode(_pin_lowerEndstop, INPUT);
  pinMode(_pin_upperEndstop, INPUT);

  pinMode(_pin_1in, OUTPUT);
  pinMode(_pin_2in, OUTPUT);
  pinMode(_pin_3in, OUTPUT);
  pinMode(_pin_4in, OUTPUT);

  pinMode(_pin_mixer, OUTPUT);

  _steppermotor.setSpeed(_speed);
}


MixerArm::ArmState MixerArm::getArmState() {
  return _armState;
}

void MixerArm::waitForPump() {
  Serial.println("Switch to 'armIsWaitingForPumpFinish'");
  _armState = armIsWaitingForPumpFinish;
}

void MixerArm::startSequence() {
  _running = true;
  _armState = armIsUnknown;
}

void MixerArm::stopSequence() {
  _running = false;
}

bool MixerArm::isRunning() {
  return _running;
}

void MixerArm::loop() {
  int stepSize = 3;

  switch (_armState) {
    case armIsWaitingForPumpFinish:
      // To Nothing
      break;

    case armIsUnknown:
      Serial.println("Switch to 'armIsGoingUp'");
      _armState = armIsGoingUp;
      break;

    case armIsUp:
      if (_running) {
        Serial.println("Switch to 'armIsGoingDown'");
        _armState = armIsGoingDown;
      }
      break;

    case armIsGoingDown:
      if (!_running) {
        _armState = armIsGoingUp;
      } else if (digitalRead(_pin_lowerEndstop) == HIGH) {
        Serial.println("Lower Endstop reached - Switch to 'armIsDown'");
        _armState = armIsDown;
      } else {
        _steppermotor.step(stepSize);
      }
      break;

    case armIsDown:
      if (!_running) {
        Serial.println("Not running, switchting to 'armIsGoingUp'");
        _armState = armIsGoingUp;
      } else {
        delay(300);
        Serial.println("Switch to 'armIsMixing'");
        _armState = armIsMixing;
      }
      break;

    case armIsMixing:
      Serial.println("Turn on mixer motor");
      digitalWrite(_pin_mixer, HIGH);
      delay(2000);  // Wait 2 seconds before switching motor off
      Serial.println("Turn off mixer motor");
      digitalWrite(_pin_mixer, LOW);
      delay(500); // Wait a bit for the motor to stop

      // After mixing, we disable running
      _running = false;
      
      Serial.println("Switch to 'armIsGoingUp'");
      _armState = armIsGoingUp;
      break;

    case armIsGoingUp:
      // XXX Not checking for _running, because going up is always allowed.
      if (digitalRead(_pin_upperEndstop) == HIGH) {
        Serial.println("Upperer Endstop reached - Switch to 'armIsUp'");
        _armState = armIsUp;
      } else {
        _steppermotor.step(-stepSize);
      }
      break;
  }
}
