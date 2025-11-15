# 🚗 K.I.T.T. CocktailMixer - Quick Start Guide

Get your Knight Rider-themed cocktail mixer up and running in 5 minutes!

## What You'll Need

- Raspberry Pi 5 with 3.5" touchscreen (480x320)
- Arduino with uploaded pump controller code
- Pumps connected and configured
- This project installed

## Quick Start (Development)

### 1. Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
python main.py
```
Backend will start on: `http://localhost:8000`

### 2. Start Frontend (Terminal 2)
```bash
cd frontend
npm start
```
Frontend will open on: `http://localhost:3000`

### 3. Configure Pumps

Edit `backend/config.yaml`:
```yaml
pumps:
  - id: 1
    liquid: "Vodka"
  - id: 2
    liquid: "Gin"
  # ... configure all pumps
```

### 4. Open in Browser

Visit: `http://localhost:3000`

You should see the red and black K.I.T.T. interface!

## Quick Start (Raspberry Pi)

### One-Command Start
```bash
./start-kitt.sh
```

This will:
1. Start the backend API
2. Serve the frontend
3. Launch Chromium in kiosk mode

### Manual Start
```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python main.py

# Terminal 2 - Frontend
cd frontend/build && python3 -m http.server 3000

# Terminal 3 - Browser
chromium-browser --kiosk --app=http://localhost:3000
```

## First Time Setup

### Install Dependencies

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
npm run build
```

### Configure Arduino

1. Open `arduino/pump_controller/pump_controller.ino`
2. Upload to Arduino
3. Note the USB port (e.g., `/dev/ttyUSB0`)
4. Update `backend/config.yaml` with the port

### Test Connection

```bash
# Check backend API
curl http://localhost:8000/status

# Should return:
# {"arduino_connected": true, "is_mixing": false, ...}
```

## Using the Interface

### Main Screen
- **ALL**: View all 200+ cocktails
- **AVAILABLE**: Only cocktails you can make
- Tap any cocktail to see details

### Cocktail Details
- View ingredients and preparation
- Select size (SMALL/MEDIUM/LARGE)
- Tap **MAKE IT** to start mixing
- Missing ingredients shown in red

### Status Screen
- Watch real-time mixing progress
- See active pumps
- Progress bar shows completion
- Automatically returns to main screen when done

## Troubleshooting

### Backend won't start
```bash
# Check Arduino connection
ls /dev/ttyUSB* /dev/ttyACM*

# Try without Arduino (testing mode)
python main.py  # Will warn but still work
```

### Frontend shows errors
```bash
# Check backend is running
curl http://localhost:8000/status

# Rebuild frontend
npm run build
```

### Touchscreen not working
```bash
# Calibrate touch
sudo apt install xinput-calibrator
DISPLAY=:0 xinput_calibrator
```

### Display resolution wrong
```bash
# Edit boot config
sudo nano /boot/config.txt

# Add:
hdmi_cvt=480 320 60 6 0 0 0
hdmi_mode=87

sudo reboot
```

## API Endpoints

- `GET /cocktails` - All cocktails with availability
- `GET /cocktails/available` - Only makeable cocktails
- `POST /cocktails/{name}/make` - Make a cocktail
- `GET /status` - System status
- `GET /docs` - API documentation

## Configuration Files

| File | Purpose |
|------|---------|
| `backend/config.yaml` | Pump configuration |
| `db/cocktails.yaml` | Cocktail recipes |
| `frontend/.env` | API URL (development) |
| `frontend/.env.production` | API URL (production) |

## Common Tasks

### Add a Cocktail
Edit `db/cocktails.yaml`:
```yaml
- name: My Custom Drink
  ingredients:
    - ingredient: Vodka
      amount: 4
      unit: cl
    - ingredient: Lime juice
      amount: 2
      unit: cl
```
Restart backend.

### Change Pump Assignment
Edit `backend/config.yaml`:
```yaml
pumps:
  - id: 1
    liquid: "Rum"  # Changed from Vodka
```
Restart backend.

### Update Frontend Theme
Edit `frontend/src/App.css`:
```css
:root {
  --kitt-red: #00ff00;  /* Change to green */
}
```
Rebuild: `npm run build`

### View Logs
```bash
# Backend logs
journalctl -u cocktail-backend -f

# Frontend logs
journalctl -u cocktail-frontend -f

# Browser logs
journalctl -u cocktail-ui -f
```

## Network Access

To access from other devices on your network:

1. Find your Pi's IP:
```bash
hostname -I
```

2. Update `frontend/.env.production`:
```
REACT_APP_API_URL=http://192.168.1.100:8000
```

3. Rebuild frontend:
```bash
npm run build
```

4. Access from phone/tablet: `http://192.168.1.100:3000`

## Safety Tips

⚠️ **Important Safety Information:**

1. **Electrical Safety**: Keep electronics away from liquids
2. **Food Safety**: Clean pumps and tubes regularly
3. **Age Verification**: For adult use only
4. **Pump Control**: Test with water first
5. **Emergency Stop**: Backend has stop_all_pumps() function

## Getting Help

**Check Status:**
```bash
# API Status
curl http://localhost:8000/status

# Services Status
systemctl status cocktail-backend cocktail-frontend cocktail-ui

# View Logs
journalctl -xe
```

**Reset Everything:**
```bash
# Stop all
sudo systemctl stop cocktail-backend cocktail-frontend cocktail-ui

# Start all
sudo systemctl start cocktail-backend cocktail-frontend cocktail-ui
```

**Complete Reboot:**
```bash
sudo reboot
```

## Documentation

- 📖 `README.md` - Project overview
- 🚀 `DEPLOYMENT.md` - Full deployment guide
- 🎨 `frontend/THEME.md` - K.I.T.T. theme design guide
- 📝 `todo.md` - Feature checklist

## Next Steps

1. ✅ Test with water first
2. ✅ Calibrate pump flow rates
3. ✅ Configure all 8 pumps
4. ✅ Add your favorite cocktails
5. ✅ Set up auto-start on boot
6. 🍸 Enjoy perfectly mixed cocktails!

---

**Need more help?** See `DEPLOYMENT.md` for detailed instructions.

**Want to customize?** See `frontend/THEME.md` for theme customization.

**Ready to deploy?** Run: `sudo systemctl enable cocktail-backend cocktail-frontend cocktail-ui`
