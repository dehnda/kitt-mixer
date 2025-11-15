# 🚗 K.I.T.T. CocktailMixer

Automated cocktail mixing machine controlled by Raspberry Pi and Arduino, featuring a K.I.T.T.-themed touchscreen interface from Knight Rider.

## 🎯 Features

- **Knight Rider Theme**: Iconic K.I.T.T. red and black interface with glowing animations
- **480x320 Touchscreen**: Optimized for 3.5" Raspberry Pi displays
- **Automated Mixing**: Control up to 8 pumps via Arduino
- **Real-time Status**: Live mixing progress and system monitoring
- **200+ Cocktails**: Extensive recipe database

## Project Structure

```
CocktailMixer/
├── backend/              # FastAPI backend
│   ├── main.py
│   ├── models/
│   ├── services/
│   ├── api/
│   ├── config.yaml
│   └── requirements.txt
├── frontend/             # React TypeScript UI (K.I.T.T. theme)
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── types/
│   └── README.md
├── arduino/              # Arduino pump controller
│   └── pump_controller/
├── db/                   # Cocktail recipes database
│   └── cocktails.yaml
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

Edit `backend/config.yaml` to assign liquids to pumps:

```yaml
pumps:
  - id: 1
    liquid: "Gin"
  - id: 2
    liquid: "Vodka"
  # ... etc
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
- PyYAML (Configuration management)

### Frontend
- React 19 with TypeScript
- Framer Motion (Animations)
- Axios (API client)
- K.I.T.T. theme (custom CSS)

## Features

### Frontend (K.I.T.T. Interface)
✅ Knight Rider themed UI with scanner animation
✅ 480x320 touchscreen optimized
✅ Real-time mixing progress visualization
✅ Cocktail browser with availability filters
✅ Size selection (Small/Medium/Large)
✅ Glowing animations and effects

### Backend
✅ RESTful API with FastAPI
✅ 200+ cocktail recipes (YAML database)
✅ Smart ingredient matching
✅ Real-time pump control via Arduino
✅ Background mixing with progress tracking
✅ Emergency stop functionality

## Screenshots

The K.I.T.T. interface features:
- 🔴 Red and black Knight Rider theme
- ⚡ Iconic scanner line animation
- 💫 Glowing text effects
- 📱 Touch-optimized buttons
- 📊 Real-time status display

Preview the interface: Open `frontend/preview.html` in a browser

## Documentation

- 📖 **README.md** (this file) - Project overview
- 🚀 **QUICKSTART.md** - Get started in 5 minutes
- 🔧 **DEPLOYMENT.md** - Complete Raspberry Pi setup guide
- 🎨 **frontend/THEME.md** - K.I.T.T. design system
- 📝 **frontend/README.md** - Frontend documentation
- 📄 **PROJECT_SUMMARY.md** - Detailed project summary

## API Endpoints

- `GET /cocktails` - List all cocktails with availability
- `GET /cocktails/available` - List only makeable cocktails
- `POST /cocktails/{name}/make` - Start making a cocktail
- `GET /status` - Get system status and progress
- `GET /docs` - Interactive API documentation

## Contributing

Feel free to:
- Add more cocktail recipes to `db/cocktails.yaml`
- Customize the K.I.T.T. theme colors
- Improve animations and effects
- Add new features (see `todo.md`)

## License

MIT
