#ifndef LedControl_h
#define LedControl_h
#include "Arduino.h"
#include <Adafruit_NeoPixel.h>

class LedControl {
public:
  enum PatternState {
    isIdling,
    isWorking,
    isError,
    isRainbow
  };

  LedControl(int pin, int numPixels, int brightness = 100);
  
  void setup();
  void loop();

  PatternState getCurrentState();

  // State control methods
  void setIdling();
  void setWorking();
  void setError();
  void setRainbow();

  // Direct pattern methods
  void idle();
  void working();
  void error();
  void rainbow();

private:
  Adafruit_NeoPixel _pixels;
  int _brightness;

  // Animation range settings
  static const int _startPixel = 8;  // First LED in animation range
  static const int _endPixel = 17;   // Last LED in animation range
  static const int _delayval = 80;

  // Idle Animation variables
  int _currentIdlePixel;
  int _currentIdleDirection;  // 1 for forward, -1 for backward

  // State management
  PatternState _patternState;  // What pattern should be shown

  // Timing variables for non-blocking animations
  unsigned long _previousMillis;
  bool _toggleState;
  uint16_t _hue;
};
#endif
