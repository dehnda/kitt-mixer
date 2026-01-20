#ifndef MixerArm_h
#define MixerArm_h
#include "Arduino.h"
#include <Stepper.h>

class MixerArm {
public:
  enum ArmState {
    armIsUnknown,
    armIsWaitingForPumpFinish,
    armIsUp,
    armIsGoingDown,
    armIsDown,
    armIsMixing,
    armIsGoingUp
  };

  MixerArm(
    int speed,
    float steps_per_revolution,
    int pin_lowerEndstop,
    int pin_upperEndstop,
    int pin_1in,
    int pin_3in,
    int pin_2in,
    int pin_4in,
    int pin_mixer);

  void setup();
  void loop();

  void startSequence();
  void stopSequence();
  void waitForPump();
  bool isRunning();
  ArmState getArmState();

private:
  int _speed;
  bool _running;
  Stepper _steppermotor;
  int _pin_1in;
  int _pin_2in;
  int _pin_3in;
  int _pin_4in;
  int _pin_lowerEndstop;
  int _pin_upperEndstop;
  int _pin_mixer;

  ArmState _armState;  // What the arm is doing at any given moment.
};
#endif
