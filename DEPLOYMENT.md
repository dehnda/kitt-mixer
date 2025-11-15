# K.I.T.T. CocktailMixer - Raspberry Pi Deployment Guide

Complete guide for deploying the K.I.T.T.-themed cocktail mixer on Raspberry Pi 5 with 3.5" touchscreen.

## Prerequisites

- Raspberry Pi 5 with Raspberry Pi OS
- 3.5" 480x320 touchscreen display
- Arduino Uno/Nano
- 8 peristaltic pumps
- 8-channel relay module
- Internet connection

## Step-by-Step Setup

### 1. Prepare Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nodejs npm chromium-browser git

# Install Node.js 18+ if needed
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. Clone/Copy Project

```bash
cd ~
# Option A: Clone from git
git clone <your-repo-url> CocktailMixer

# Option B: Copy from USB/network
# scp -r user@host:/path/to/CocktailMixer ~/
```

### 3. Setup Backend

```bash
cd ~/CocktailMixer/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Arduino port (find your port first)
ls /dev/ttyUSB* /dev/ttyACM*
# Edit config.yaml and set the correct port
nano config.yaml
```

Edit `config.yaml`:
```yaml
arduino:
  port: "/dev/ttyUSB0"  # or /dev/ttyACM0
  baudrate: 9600

pumps:
  - id: 1
    pin: 2
    ml_per_second: 10.0
    liquid: "Vodka"
  # Configure all 8 pumps...
```

Test backend:
```bash
python main.py
# Should start on http://0.0.0.0:8000
# Press Ctrl+C to stop
```

### 4. Setup Frontend

```bash
cd ~/CocktailMixer/frontend

# Install dependencies
npm install

# Configure API URL (use your Pi's IP)
echo "REACT_APP_API_URL=http://localhost:8000" > .env.production

# Build for production
npm run build
```

### 5. Configure Display

Edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add/modify these lines for 480x320 display:
```
# Display settings
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=480 320 60 6 0 0 0
display_rotate=0

# Touchscreen
dtoverlay=ads7846,cs=1,penirq=25,penirq_pull=2,speed=50000,keep_vref_on=0,swapxy=0,pmax=255,xohms=150,xmin=200,xmax=3900,ymin=200,ymax=3900
```

Reboot:
```bash
sudo reboot
```

### 6. Test Touchscreen

```bash
sudo apt install -y xinput-calibrator
DISPLAY=:0 xinput_calibrator
```

Follow on-screen instructions to calibrate touch input.

### 7. Create Systemd Services

#### Backend Service

Create `/etc/systemd/system/cocktail-backend.service`:
```bash
sudo nano /etc/systemd/system/cocktail-backend.service
```

```ini
[Unit]
Description=K.I.T.T. Cocktail Mixer Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/CocktailMixer/backend
Environment="PATH=/home/pi/CocktailMixer/backend/venv/bin:/usr/bin"
ExecStart=/home/pi/CocktailMixer/backend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Frontend Service

Create `/etc/systemd/system/cocktail-frontend.service`:
```bash
sudo nano /etc/systemd/system/cocktail-frontend.service
```

```ini
[Unit]
Description=K.I.T.T. Cocktail Mixer Frontend
After=network.target cocktail-backend.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/CocktailMixer/frontend/build
ExecStart=/usr/bin/python3 -m http.server 3000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Chromium Kiosk Service

Create `/etc/systemd/system/cocktail-ui.service`:
```bash
sudo nano /etc/systemd/system/cocktail-ui.service
```

```ini
[Unit]
Description=K.I.T.T. Cocktail Mixer UI
After=graphical.target cocktail-frontend.service
Wants=graphical.target

[Service]
Type=simple
User=pi
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
ExecStartPre=/bin/sleep 5
ExecStart=/usr/bin/chromium-browser --kiosk --app=http://localhost:3000 \
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
  --touch-events=enabled \
  --no-first-run \
  --fast --fast-start \
  --disable-features=TranslateUI
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
```

### 8. Enable and Start Services

```bash
# Enable services to start on boot
sudo systemctl enable cocktail-backend
sudo systemctl enable cocktail-frontend
sudo systemctl enable cocktail-ui

# Start services now
sudo systemctl start cocktail-backend
sudo systemctl start cocktail-frontend
sudo systemctl start cocktail-ui

# Check status
sudo systemctl status cocktail-backend
sudo systemctl status cocktail-frontend
sudo systemctl status cocktail-ui
```

### 9. Auto-start on Boot

Edit autostart:
```bash
mkdir -p ~/.config/lxsession/LXDE-pi
nano ~/.config/lxsession/LXDE-pi/autostart
```

Add:
```
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xscreensaver -no-splash
@xset s off
@xset -dpms
@xset s noblank
@unclutter -idle 0
```

### 10. Disable Screen Blanking

```bash
# Edit lightdm config
sudo nano /etc/lightdm/lightdm.conf
```

Add under `[Seat:*]`:
```
xserver-command=X -s 0 -dpms
```

### 11. Hide Mouse Cursor

```bash
sudo apt install -y unclutter
```

Add to autostart (already added in step 9):
```
@unclutter -idle 0
```

## Testing

### Manual Test
```bash
# Terminal 1
cd ~/CocktailMixer/backend
source venv/bin/activate
python main.py

# Terminal 2
cd ~/CocktailMixer/frontend/build
python3 -m http.server 3000

# Terminal 3
DISPLAY=:0 chromium-browser --kiosk --app=http://localhost:3000
```

### Service Test
```bash
# Check all services are running
systemctl status cocktail-backend cocktail-frontend cocktail-ui

# View logs
journalctl -u cocktail-backend -f
journalctl -u cocktail-frontend -f
journalctl -u cocktail-ui -f
```

## Troubleshooting

### Backend won't connect to Arduino
```bash
# Check Arduino port
ls -l /dev/ttyUSB* /dev/ttyACM*

# Add user to dialout group
sudo usermod -a -G dialout pi
# Logout and login again

# Check permissions
sudo chmod 666 /dev/ttyUSB0  # or ttyACM0
```

### Frontend can't connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/status

# Check firewall
sudo ufw status
sudo ufw allow 8000
sudo ufw allow 3000
```

### Touchscreen not working
```bash
# Check input devices
xinput list

# Calibrate
DISPLAY=:0 xinput_calibrator

# Apply calibration (follow calibrator output)
```

### Display resolution wrong
```bash
# Check current settings
tvservice -s

# Force resolution
sudo nano /boot/config.txt
# Add: hdmi_cvt=480 320 60 6 0 0 0
sudo reboot
```

### Chromium won't start in kiosk
```bash
# Check X11 display
echo $DISPLAY  # Should be :0

# Test manually
DISPLAY=:0 chromium-browser --version

# Check logs
journalctl -u cocktail-ui -n 50
```

### Services won't start on boot
```bash
# Check service status
sudo systemctl status cocktail-backend

# Check dependencies
systemctl list-dependencies cocktail-ui

# Re-enable
sudo systemctl disable cocktail-ui
sudo systemctl enable cocktail-ui
```

## Maintenance

### Update cocktail recipes
```bash
nano ~/CocktailMixer/db/cocktails.yaml
sudo systemctl restart cocktail-backend
```

### Update frontend
```bash
cd ~/CocktailMixer/frontend
# Make changes
npm run build
sudo systemctl restart cocktail-frontend
# Refresh browser (Ctrl+R in kiosk)
```

### Update backend
```bash
cd ~/CocktailMixer/backend
source venv/bin/activate
# Make changes
sudo systemctl restart cocktail-backend
```

### View logs
```bash
# Recent logs
sudo journalctl -u cocktail-backend --since "1 hour ago"
sudo journalctl -u cocktail-frontend --since "1 hour ago"

# Follow logs live
sudo journalctl -u cocktail-backend -f
```

### Backup configuration
```bash
cd ~
tar -czf cocktail-mixer-backup.tar.gz \
  CocktailMixer/backend/config.yaml \
  CocktailMixer/db/cocktails.yaml \
  CocktailMixer/frontend/.env.production
```

## Performance Tips

1. **Disable unnecessary services:**
```bash
sudo systemctl disable bluetooth
sudo systemctl disable triggerhappy
```

2. **Optimize Chromium:**
   - Already optimized in service file
   - Uses hardware acceleration when available

3. **Use lightweight desktop:**
   - Already using LXDE (default on Raspberry Pi OS)

4. **Reduce logging:**
```bash
# Edit backend main.py to reduce log verbosity
```

## Security

For production use:

1. **Change default passwords:**
```bash
passwd
```

2. **Enable firewall:**
```bash
sudo apt install ufw
sudo ufw enable
sudo ufw allow 22    # SSH
sudo ufw allow 8000  # Backend (local only)
```

3. **Update CORS settings** in `backend/main.py`:
```python
allow_origins=["http://localhost:3000"]  # Instead of ["*"]
```

4. **Disable SSH** if not needed:
```bash
sudo systemctl disable ssh
```

## Support

For issues or questions:
- Check logs: `journalctl -u cocktail-* -f`
- Test components individually
- Verify hardware connections
- Check backend API: http://localhost:8000/docs

## Quick Commands Reference

```bash
# Start all services
sudo systemctl start cocktail-backend cocktail-frontend cocktail-ui

# Stop all services
sudo systemctl stop cocktail-backend cocktail-frontend cocktail-ui

# Restart all services
sudo systemctl restart cocktail-backend cocktail-frontend cocktail-ui

# View all logs
sudo journalctl -u cocktail-backend -u cocktail-frontend -u cocktail-ui -f

# Rebuild frontend
cd ~/CocktailMixer/frontend && npm run build && sudo systemctl restart cocktail-frontend

# Reboot system
sudo reboot
```
