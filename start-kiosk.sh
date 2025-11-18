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
    if curl -s "$BACKEND_URL/api/status" > /dev/null 2>&1; then
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
    xset s off
    xset -dpms
    xset s noblank
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

chromium-browser \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --no-first-run \
    --disable-restore-session-state \
    --disable-session-crashed-bubble \
    --disable-features=TranslateUI \
    --disable-component-extensions-with-background-pages \
    --app="$FRONTEND_URL" \
    > "$LOG_DIR/chromium.log" 2>&1

# When Chromium closes, cleanup
cleanup
