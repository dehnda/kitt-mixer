#include "Arduino.h"
#include "LedControl.h"
#include <Adafruit_NeoPixel.h>

LedControl::LedControl(int pin, int numPixels, int brightness)
  : _pixels(numPixels, pin, NEO_GRB + NEO_KHZ800) {
  _brightness = brightness;
  _currentIdlePixel = _startPixel;
  _currentIdleDirection = 1;
  _patternState = isIdling;
  _previousMillis = 0;
  _toggleState = false;
  _hue = 0;
}

void LedControl::setup() {
  _pixels.begin();
  _pixels.clear();
  _pixels.setBrightness(_brightness);
  _currentIdlePixel = _startPixel;
}

void LedControl::loop() {
  // Clear all pixels first
  _pixels.clear();

  switch (_patternState) {
    case isIdling:
      idle();
      break;

    case isWorking:
      working();
      break;

    case isError:
      error();
      break;

    case isRainbow:
      rainbow();
      break;
  }
}

LedControl::PatternState LedControl::getCurrentState() {
  return _patternState;
}

void LedControl::setIdling() {
  _patternState = isIdling;
}

void LedControl::setWorking() {
  _patternState = isWorking;
}

void LedControl::setError() {
  _patternState = isError;
}

void LedControl::setRainbow() {
  _patternState = isRainbow;
}

void LedControl::idle() {
  static unsigned long lastUpdate = 0;
  unsigned long currentMillis = millis();

  if (currentMillis - lastUpdate >= _delayval) {
    lastUpdate = currentMillis;

    // Set the main bright pixel (KITT red)
    _pixels.setPixelColor(_currentIdlePixel, _pixels.Color(255, 0, 0));

    // Add trailing fade effect
    if (_currentIdlePixel - _currentIdleDirection >= _startPixel && _currentIdlePixel - _currentIdleDirection <= _endPixel) {
      _pixels.setPixelColor(_currentIdlePixel - _currentIdleDirection, _pixels.Color(125, 0, 0));
    }
    if (_currentIdlePixel - (2 * _currentIdleDirection) >= _startPixel && _currentIdlePixel - (2 * _currentIdleDirection) <= _endPixel) {
      _pixels.setPixelColor(_currentIdlePixel - (2 * _currentIdleDirection), _pixels.Color(62, 0, 0));
    }
    if (_currentIdlePixel - (3 * _currentIdleDirection) >= _startPixel && _currentIdlePixel - (3 * _currentIdleDirection) <= _endPixel) {
      _pixels.setPixelColor(_currentIdlePixel - (3 * _currentIdleDirection), _pixels.Color(31, 0, 0));
    }

    _pixels.show();

    // Move to next position
    _currentIdlePixel += _currentIdleDirection;

    // Reverse direction at the custom range ends
    if (_currentIdlePixel >= _endPixel || _currentIdlePixel <= _startPixel) {
      _currentIdleDirection = -_currentIdleDirection;
    }
  }
}

void LedControl::working() {
  unsigned long currentMillis = millis();

  if (currentMillis - _previousMillis >= 250) {
    _previousMillis = currentMillis;
    _toggleState = !_toggleState;
  }

  // Light up LEDs based on odd/even pattern
  for (int i = 0; i < _pixels.numPixels(); i++) {
    if ((_toggleState && i % 2 == 0) || (!_toggleState && i % 2 == 1)) {
      _pixels.setPixelColor(i, _pixels.Color(255, 125, 0));  // Yellow
    } else {
      _pixels.setPixelColor(i, _pixels.Color(0, 0, 0));  // Off
    }
  }

  _pixels.show();
}

void LedControl::error() {
  unsigned long currentMillis = millis();

  if (currentMillis - _previousMillis >= 500) {
    _previousMillis = currentMillis;
    _toggleState = !_toggleState;
  }

  // Set all LEDs to red or off
  for (int i = 0; i < _pixels.numPixels(); i++) {
    if (_toggleState) {
      _pixels.setPixelColor(i, _pixels.Color(255, 0, 0));  // Red
    } else {
      _pixels.setPixelColor(i, _pixels.Color(0, 0, 0));  // Off
    }
  }

  _pixels.show();
}

void LedControl::rainbow() {
  unsigned long currentMillis = millis();

  if (currentMillis - _previousMillis >= 20) {
    _previousMillis = currentMillis;

    for (int i = 0; i < _pixels.numPixels(); i++) {
      // Calculate hue for each pixel with offset
      uint16_t pixelHue = _hue + (i * (uint16_t)(65536L / _pixels.numPixels()));
      _pixels.setPixelColor(i, _pixels.gamma32(_pixels.ColorHSV(pixelHue)));
    }

    _pixels.show();
    _hue += 256;  // Increment hue for animation (will naturally wrap at 65536)
  }
}
