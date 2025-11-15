#!/bin/bash

# Start script for the K.I.T.T. Cocktail Mixer Frontend
# Run this on your Raspberry Pi

echo "Starting K.I.T.T. Cocktail Mixer..."

# Set display for X11
export DISPLAY=:0

# Start backend in background
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend in kiosk mode
cd ../frontend/build
python3 -m http.server 3000 &
FRONTEND_PID=$!

# Wait for frontend server to start
sleep 2

# Launch Chromium in kiosk mode
chromium-browser --kiosk --app=http://localhost:3000 \
  --window-size=480,320 \
  --window-position=0,0 \
  --force-device-scale-factor=1 \
  --disable-pinch \
  --overscroll-history-navigation=0 \
  --noerrdialogs \
  --disable-suggestions-service \
  --disable-translate \
  --disable-save-password-bubble \
  --disable-session-crashed-bubble \
  --disable-infobars \
  --touch-events=enabled

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
