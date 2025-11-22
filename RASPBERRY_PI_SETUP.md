# Raspberry Pi Kiosk Mode Setup

This guide will help you set up the K.I.T.T. Cocktail Mixer to run in kiosk mode on a Raspberry Pi.

## Prerequisites

- Raspberry Pi (3B+ or newer recommended)
- Raspberry Pi OS (32-bit or 64-bit)
- 320x480 portrait display connected
- Internet connection for initial setup

## Initial Setup

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    chromium-browser \
    x11-xserver-utils \
    unclutter \
    wlr-randr \
    git
```

### 2. Clone the Project

```bash
cd ~
git clone https://github.com/dehnda/kitt-mixer.git CocktailMixer
cd CocktailMixer
```

### 3. Setup Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
```

### 4. Setup Frontend

```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. Install Frontend Serve Tool

```bash
sudo npm install -g serve
```

### 6. Configure Display Rotation (for portrait mode)

Edit `/boot/config.txt`:

```bash
sudo nano /boot/config.txt
```

Add the following line to rotate the display to portrait mode:

```
# For 90° rotation (portrait)
wlr-randr --output DSI-1 --transform 270
```

Reboot for changes to take effect:

```bash
sudo reboot
```

### 7. Make the Kiosk Script Executable

```bash
chmod +x start-kiosk.sh
```

## Test the Kiosk Mode

Before setting up autostart, test the script manually:

```bash
./start-kiosk.sh
```

Press `Ctrl+C` to exit and stop all services.

## Setup Autostart

### Option 1: Using Autostart (LXDE/Pixel Desktop)

1. Create autostart directory if it doesn't exist:

```bash
mkdir -p ~/.config/autostart
```

2. Copy the desktop file (update the path if needed):

```bash
cp kitt-mixer.desktop ~/.config/autostart/
```

3. Edit the desktop file to match your installation path:

```bash
nano ~/.config/autostart/kitt-mixer.desktop
```

Update the `Exec` line to your actual path:
```
Exec=/home/pi/CocktailMixer/start-kiosk.sh
```

### Option 2: Using systemd (runs on boot, no desktop required)

1. Create a systemd service file:

```bash
sudo nano /etc/systemd/system/kitt-mixer.service
```

2. Add the following content (update paths as needed):

```ini
[Unit]
Description=K.I.T.T. Cocktail Mixer Kiosk
After=graphical.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
WorkingDirectory=/home/pi/CocktailMixer
ExecStart=/home/pi/CocktailMixer/start-kiosk.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=graphical.target
```

3. Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable kitt-mixer.service
sudo systemctl start kitt-mixer.service
```

4. Check service status:

```bash
sudo systemctl status kitt-mixer.service
```

## Arduino Connection

The application will automatically detect if an Arduino is connected. If not, it will run in simulation mode.

To connect an Arduino:

1. Connect Arduino via USB
2. The backend will automatically detect it on `/dev/ttyUSB0` or `/dev/ttyACM0`
3. If connection is lost, it will auto-reconnect (up to 3 attempts)

## Display Configuration

The application is designed for a **320x480 portrait display**. If you have a different display size, you may need to adjust the CSS in:

- `frontend/src/App.css` - Main container dimensions
- `frontend/src/components/*.css` - Component layouts

## Troubleshooting

### Check Logs

Logs are stored in the `logs/` directory:

```bash
tail -f logs/backend.log
tail -f logs/frontend.log
tail -f logs/chromium.log
```

### Backend Won't Start

```bash
cd backend
source venv/bin/activate
python main.py
```

Check for error messages and ensure all dependencies are installed.

### Frontend Won't Build

```bash
cd frontend
npm install
npm run build
```

### Chromium Won't Start in Kiosk Mode

Ensure X server is running:
```bash
echo $DISPLAY  # Should show :0
```

### Screen Blanking Issues

The script disables screen blanking automatically, but you can also set it in Raspberry Pi Configuration:

```bash
sudo raspi-config
# Display Options → Screen Blanking → No
```

### Cursor Visible

Install unclutter if not already installed:
```bash
sudo apt-get install unclutter
```

## Performance Tips

1. **Overclock** (if using Pi 3 or older):
   Edit `/boot/config.txt` and add:
   ```
   arm_freq=1400
   gpu_freq=500
   ```

2. **Reduce GPU memory** (if not using camera):
   ```
   gpu_mem=128
   ```

3. **Disable unnecessary services**:
   ```bash
   sudo systemctl disable bluetooth
   sudo systemctl disable cups
   ```

## Updating the Application

To update the application:

```bash
cd ~/CocktailMixer
git pull
cd frontend
npm install
npm run build
cd ..
```

Then restart the kiosk:
```bash
sudo systemctl restart kitt-mixer.service
```

## Manual Control

### Start Kiosk Mode
```bash
./start-kiosk.sh
```

### Stop Services (if running manually)
Press `Ctrl+C` in the terminal running the script.

### Stop systemd Service
```bash
sudo systemctl stop kitt-mixer.service
```

## Security Notes

- The application runs on localhost only by default
- If you need network access, configure firewall rules appropriately
- Change default passwords if exposing to network
- Consider disabling SSH if not needed for security

## Support

For issues or questions, check the project repository:
https://github.com/dehnda/kitt-mixer
