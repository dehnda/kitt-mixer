# 🚗 K.I.T.T. CocktailMixer

Automated cocktail mixing machine controlled by Raspberry Pi and Arduino, featuring a K.I.T.T.-themed touchscreen interface from Knight Rider.

## 🎯 Features

- **Knight Rider Theme**: Iconic K.I.T.T. red/orange/yellow color scheme with glowing animations
- **480x320 Touchscreen**: Optimized for 3.5" Raspberry Pi displays
- **Automated Mixing**: Control up to 8 pumps via Arduino
- **Real-time Status**: Live mixing progress and system monitoring
- **75+ Cocktails**: Curated recipe database with 83 liquids
- **Smart Availability**: Automatic cocktail filtering based on installed liquids
- **SQLite Database**: Proper relational database with normalized schema

## Project Structure

```
CocktailMixer/
├── backend/              # FastAPI backend
│   ├── main.py
│   ├── database/
│   │   ├── schema.sql        # SQLite schema
│   │   ├── db_manager.py     # Database manager
│   │   └── migrate.py        # YAML to SQLite migration
│   ├── models/
│   ├── services/
│   │   ├── arduino.py        # Arduino communication
│   │   ├── database.py       # Database service
│   │   └── mixer.py          # Mixing logic
│   ├── api/
│   │   ├── cocktails.py
│   │   ├── liquids.py
│   │   ├── pumps.py
│   │   └── status.py
│   └── requirements.txt
├── frontend/             # React TypeScript UI (K.I.T.T. theme)
│   ├── src/
│   │   ├── components/
│   │   │   ├── CocktailList.tsx      # Main selection screen
│   │   │   ├── ConfigScreen.tsx      # Pump configuration
│   │   │   ├── StatusScreen.tsx      # System status
│   │   │   └── CalibrateScreen.tsx   # Pump calibration
│   │   ├── services/
│   │   └── types/
│   └── README.md
├── arduino/              # Arduino pump controller
│   └── pump_controller/
├── db/                   # Database
│   └── cocktails.db      # SQLite database (78 liquids, 76 cocktails, 8 pumps)
└── start-kitt.sh        # Launch script for Raspberry Pi
```

## Quick Start

### 1. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

### 2. Setup Frontend

```bash
cd frontend
npm install
npm run build
```

### 3. Upload Arduino Code

Open `arduino/pump_controller/pump_controller.ino` in Arduino IDE and upload to your Arduino board.

### 4. Configure Pumps

Use the CONFIG screen in the UI to assign liquids to pumps, or use the API:

```bash
curl -X PUT http://localhost:8000/api/v1/pumps/1 \
  -H "Content-Type: application/json" \
  -d '{"liquid_id": 16, "ml_per_second": 2.5}'
```

View available liquids:
```bash
curl http://localhost:8000/api/v1/liquids
```

### 5. Launch K.I.T.T. Interface (Raspberry Pi)

```bash
./start-kitt.sh
```

Or manually:
```bash
# Terminal 1 - Backend
cd backend && source venv/bin/activate && python main.py

# Terminal 2 - Frontend
cd frontend/build && python3 -m http.server 3000

# Terminal 3 - Browser (kiosk mode)
chromium-browser --kiosk --app=http://localhost:3000
```

### 6. Access API

- K.I.T.T. UI: http://localhost:3000
- Swagger docs: http://localhost:8000/docs
- API: http://localhost:8000

## Hardware Requirements

- **Raspberry Pi 5** with 3.5" 480x320 touchscreen
- **Arduino Uno/Nano**
- 8-channel relay module
- 8 peristaltic pumps (12V recommended)
- Power supply for pumps (12V, 2-3A)
- USB cable (Raspberry Pi ↔ Arduino)
- Bottles and tubing

## Software Stack

### Backend
- FastAPI (Python web framework)
- PySerial (Arduino communication)
- SQLite (Database)
- Pydantic (Data validation)

### Frontend
- React 19 with TypeScript
- Framer Motion (Animations)
- Axios (API client)
- K.I.T.T. theme (custom CSS with red/orange/yellow/green color scheme)

## Features

### Frontend (K.I.T.T. Interface)
✅ Knight Rider themed UI with color-coded buttons
✅ 480x320 touchscreen optimized
✅ Cocktail selection with ingredient panel (toggleable)
✅ Smart availability filtering (green/red indicators)
✅ Pump configuration screen with inline editing
✅ Calibration interface with flow rate calculation
✅ System status with diagnostics
✅ Glowing animations and effects
✅ Hidden scrollbars for clean interface

### Backend
✅ RESTful API with FastAPI
✅ SQLite database with normalized schema
✅ ID-based liquid identification (case-insensitive)
✅ 75+ cocktail recipes, 83 liquids
✅ Smart ingredient matching
✅ Real-time pump control via Arduino
✅ Pump testing and calibration endpoints
✅ Purge all pumps functionality
✅ System diagnostics endpoint
✅ Emergency stop functionality

### Button Color Scheme
- 🟢 **Green**: Positive actions (ENGAGE, SAVE, STATUS)
- 🟡 **Yellow**: Testing/Calibration (RUN TEST, CALIBRATE, PURGE, TEST ALL)
- 🟠 **Orange**: Configuration (CONFIG, DIAGNOSTICS)
- 🔴 **Red**: Danger/Cancel (CANCEL, EMERGENCY)
- ⚪ **Default**: Navigation (BACK, REFRESH, CALCULATE)

## Screenshots

The K.I.T.T. interface features:
- 🔴 Red/orange/yellow Knight Rider color scheme
- 💫 Glowing text effects and animations
- 📱 Touch-optimized buttons with color-coded actions
- 📊 Real-time status display with diagnostics
- 🍹 Cocktail browser with toggleable ingredient panel
- ⚙️ Inline pump configuration and calibration
- 🎯 Smart availability indicators

Preview the interface: Open `frontend/preview.html` in a browser

## Database

The project uses SQLite with a normalized schema:

**Tables:**
- `liquids` - All available liquids (83 entries)
- `pumps` - Pump configurations (8 pumps)
- `cocktails` - Cocktail recipes (76 entries)
- `cocktail_ingredients` - Recipe ingredients with amounts
- `calibrations` - Pump calibration history
- `mix_history` - Cocktail mixing history
- `settings` - System settings

**Migration from YAML:**
The original YAML-based system has been migrated to SQLite. See `backend/database/migrate.py` for the migration script.

## Documentation

- 📖 **README.md** (this file) - Project overview
- 🚀 **QUICKSTART.md** - Get started in 5 minutes
- 🔧 **DEPLOYMENT.md** - Complete Raspberry Pi setup guide
- 🎨 **frontend/THEME.md** - K.I.T.T. design system
- 📝 **frontend/README.md** - Frontend documentation
- 📄 **PROJECT_SUMMARY.md** - Detailed project summary

## API Endpoints

### Cocktails
- `GET /api/v1/cocktails` - List all cocktails with availability
- `GET /api/v1/cocktails/available` - List only makeable cocktails
- `GET /api/v1/cocktails/{name}` - Get specific cocktail details
- `POST /api/v1/cocktails/{name}/make` - Start making a cocktail

### Liquids
- `GET /api/v1/liquids` - List all available liquids
- `GET /api/v1/liquids/installed` - List installed liquids

### Pumps
- `GET /api/v1/pumps` - List all pumps with assigned liquids
- `GET /api/v1/pumps/{id}` - Get specific pump details
- `PUT /api/v1/pumps/{id}` - Update pump (liquid_id, ml_per_second)
- `POST /api/v1/pumps/{id}/test` - Test pump for duration
- `POST /api/v1/pumps/test-all` - Test all pumps sequentially
- `POST /api/v1/pumps/purge-all` - Purge all pumps with liquids

### Status
- `GET /api/v1/status` - Get system status and progress
- `GET /api/v1/status/diagnostics` - Run system diagnostics
- `POST /api/v1/status/cancel` - Cancel current mixing operation
- `POST /api/v1/status/emergency-stop` - Emergency stop all pumps

### Documentation
- `GET /docs` - Interactive Swagger API documentation
- `GET /redoc` - ReDoc API documentation

## Contributing

Feel free to:
- Add more cocktail recipes to the database
- Customize the K.I.T.T. theme colors
- Improve animations and effects
- Add new features
- Submit pull requests

## Recent Updates

- ✅ Migrated from YAML to SQLite database
- ✅ Implemented ID-based liquid system (eliminates case-sensitivity issues)
- ✅ Added toggleable ingredient panel in cocktail selection
- ✅ Implemented color-coded button scheme (green/yellow/orange/red)
- ✅ Added pump testing and purge functionality
- ✅ Added system diagnostics endpoint
- ✅ Improved UI with smart availability indicators
- ✅ Enhanced calibration interface

## License

MIT

---

**Built with ❤️ for Knight Rider fans and cocktail enthusiasts**
