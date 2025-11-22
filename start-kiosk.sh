#!/bin/bash
# K.I.T.T. Cocktail Mixer - Raspberry Pi Kiosk Mode Launcher
# This script starts the backend, frontend, and launches Chromium in kiosk mode

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
LOG_DIR="$SCRIPT_DIR/logs"
FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:8000"

# Create logs directory
mkdir -p "$LOG_DIR"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}K.I.T.T. Cocktail Mixer - Kiosk Mode${NC}"
echo -e "${GREEN}========================================${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Kill any existing processes to avoid conflicts
echo -e "${YELLOW}Checking for existing processes...${NC}"
pkill -f "python.*main.py" 2>/dev/null && echo -e "${YELLOW}Killed existing backend process${NC}"
pkill -f "serve.*build" 2>/dev/null && echo -e "${YELLOW}Killed existing frontend process${NC}"
pkill -f "chromium.*kiosk" 2>/dev/null && echo -e "${YELLOW}Killed existing Chromium process${NC}"
sleep 2

# Check if backend virtual environment exists
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${RED}Error: Backend virtual environment not found${NC}"
    echo -e "${YELLOW}Please run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

# Check if frontend build exists
if [ ! -d "$FRONTEND_DIR/build" ]; then
    echo -e "${YELLOW}Frontend build not found. Building...${NC}"
    cd "$FRONTEND_DIR"
    npm install
    npm run build
    if [ $? -ne 0 ]; then
        echo -e "${RED}Frontend build failed${NC}"
        exit 1
    fi
    cd "$SCRIPT_DIR"
fi

# Start backend
echo -e "${GREEN}Starting backend server...${NC}"
cd "$BACKEND_DIR"
source venv/bin/activate
python main.py > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s "$BACKEND_URL/api/v1/status" > /dev/null 2>&1; then
        echo -e "${GREEN}Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}Backend failed to start${NC}"
        echo -e "${YELLOW}Check logs at: $LOG_DIR/backend.log${NC}"
        cleanup
    fi
    sleep 1
done

# Start frontend server (using serve package)
echo -e "${GREEN}Starting frontend server...${NC}"
cd "$FRONTEND_DIR"

# Check if serve is installed globally, if not use npx
if command -v serve &> /dev/null; then
    serve -s build -l 3000 > "$LOG_DIR/frontend.log" 2>&1 &
else
    npx serve -s build -l 3000 > "$LOG_DIR/frontend.log" 2>&1 &
fi
FRONTEND_PID=$!
echo -e "${GREEN}Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to be ready
echo -e "${YELLOW}Waiting for frontend to start...${NC}"
for i in {1..15}; do
    if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
        echo -e "${GREEN}Frontend is ready!${NC}"
        break
    fi
    if [ $i -eq 15 ]; then
        echo -e "${RED}Frontend failed to start${NC}"
        echo -e "${YELLOW}Check logs at: $LOG_DIR/frontend.log${NC}"
        cleanup
    fi
    sleep 1
done

# Disable screen blanking and power management (if xset is available)
if command -v xset &> /dev/null; then
    echo -e "${GREEN}Disabling screen blanking...${NC}"
    # Try to disable screen blanking, but don't fail if display doesn't support it
    xset s off 2>/dev/null || true
    xset -dpms 2>/dev/null || true
    xset s noblank 2>/dev/null || true
    echo -e "${GREEN}Screen blanking settings applied (if supported by display)${NC}"
else
    echo -e "${YELLOW}xset not found - screen blanking settings not changed${NC}"
    echo -e "${YELLOW}Install with: sudo apt-get install x11-xserver-utils${NC}"
fi

# Hide cursor after 1 second of inactivity (optional)
if command -v unclutter &> /dev/null; then
    unclutter -idle 1 &
else
    echo -e "${YELLOW}unclutter not found - cursor will remain visible${NC}"
    echo -e "${YELLOW}Install with: sudo apt-get install unclutter${NC}"
fi

# Launch Chromium in kiosk mode
echo -e "${GREEN}Launching Chromium in kiosk mode...${NC}"
sleep 2  # Give everything a moment to stabilize

# Check if we have a display, if not set it to :0 (primary display)
if [ -z "$DISPLAY" ]; then
    echo -e "${YELLOW}No DISPLAY set, using :0 (primary display)${NC}"
    export DISPLAY=:0
fi

# Find Chromium binary (different names on different systems)
CHROMIUM_CMD=""
if command -v chromium-browser &> /dev/null; then
    CHROMIUM_CMD="chromium-browser"
elif command -v chromium &> /dev/null; then
    CHROMIUM_CMD="chromium"
elif command -v google-chrome &> /dev/null; then
    CHROMIUM_CMD="google-chrome"
else
    echo -e "${RED}Error: No Chromium or Chrome browser found${NC}"
    echo -e "${YELLOW}Install with: sudo apt-get install chromium-browser${NC}"
    echo -e "${YELLOW}Or: sudo apt-get install chromium${NC}"
    cleanup
fi

echo -e "${GREEN}Display: $DISPLAY${NC}"
echo -e "${GREEN}Browser found: $CHROMIUM_CMD${NC}"
echo -e "${GREEN}Starting browser in kiosk mode...${NC}"

$CHROMIUM_CMD \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --no-first-run \
    --disable-restore-session-state \
    --disable-session-crashed-bubble \
    --disable-features=TranslateUI \
    --disable-component-extensions-with-background-pages \
    --password-store=basic \
    --disable-password-manager-reauthentication \
    --no-default-browser-check \
    --disable-background-networking \
    --disable-sync \
    --metrics-recording-only \
    --disable-default-apps \
    --mute-audio \
    --app="$FRONTEND_URL" \
    > "$LOG_DIR/chromium.log" 2>&1

CHROMIUM_EXIT=$?
echo -e "${YELLOW}Chromium exited with code: $CHROMIUM_EXIT${NC}"
if [ $CHROMIUM_EXIT -ne 0 ]; then
    echo -e "${RED}Chromium exited with an error. Check logs at: $LOG_DIR/chromium.log${NC}"
fi

# When Chromium closes, cleanup
cleanup
