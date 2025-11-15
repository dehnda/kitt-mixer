# CocktailMixer Backend

FastAPI-based backend for the CocktailMixer machine that runs on Raspberry Pi.

## Features

- **Pump Control**: Manage 8 pumps via Arduino
- **Cocktail Database**: YAML-based recipe storage
- **Smart Matching**: Only shows cocktails you can make with installed liquids
- **RESTful API**: Complete API for frontend integration
- **Serial Communication**: Direct Arduino control via USB

## Tech Stack

- Python 3.9+
- FastAPI
- PySerial (Arduino communication)
- PyYAML (database)
- Uvicorn (ASGI server)

## Installation

### 1. Clone and Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and adjust settings:

```bash
cp .env.example .env
```

Edit `.env`:
```env
HOST=0.0.0.0
PORT=8000
DEBUG=True
COCKTAILS_DB_PATH=../db/cocktails.yaml
CONFIG_PATH=./config.yaml
ARDUINO_PORT=/dev/ttyUSB0  # On Raspberry Pi
ARDUINO_BAUDRATE=9600
```

### 3. Configure Pumps

Edit `config.yaml` to set up your pumps:

```yaml
pumps:
  - id: 1
    pin: 2
    ml_per_second: 10.0
    liquid: "Vodka"
  - id: 2
    pin: 3
    ml_per_second: 10.0
    liquid: "Gin"
  # ... etc
```

### 4. Upload Arduino Sketch

Upload `arduino/pump_controller/pump_controller.ino` to your Arduino.

### 5. Run the Server

```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Pumps
- `GET /api/v1/pumps` - List all pumps
- `GET /api/v1/pumps/{pump_id}` - Get pump details
- `PUT /api/v1/pumps/{pump_id}/liquid` - Assign liquid to pump

### Cocktails
- `GET /api/v1/cocktails` - List all cocktails with availability
- `GET /api/v1/cocktails/available` - List only makeable cocktails
- `GET /api/v1/cocktails/{name}` - Get cocktail details
- `POST /api/v1/cocktails/{name}/make` - Make a cocktail

### Status
- `GET /api/v1/status` - Get current mixer status
- `POST /api/v1/status/cancel` - Cancel current operation
- `POST /api/v1/status/emergency-stop` - Emergency stop all pumps

### Liquids
- `GET /api/v1/liquids` - Get all available liquids
- `GET /api/v1/liquids/installed` - Get installed liquids

## Project Structure

```
backend/
├── main.py              # FastAPI application entry
├── config.yaml          # Pump configuration
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── models/
│   └── __init__.py     # Pydantic models
├── services/
│   ├── __init__.py
│   ├── database.py     # YAML data access
│   ├── arduino.py      # Serial communication
│   └── mixer.py        # Mixing logic
└── api/
    ├── __init__.py
    ├── pumps.py        # Pump endpoints
    ├── cocktails.py    # Cocktail endpoints
    ├── status.py       # Status endpoints
    └── liquids.py      # Liquid endpoints
```

## Development

### Testing Arduino Connection

```bash
python -c "from services.arduino import ArduinoService; a = ArduinoService('/dev/ttyUSB0'); a.connect(); print(a.get_status()); a.disconnect()"
```

### Testing Database

```bash
python -c "from services.database import DatabaseService; db = DatabaseService('../db/cocktails.yaml', 'config.yaml'); print(len(db.get_cocktails()), 'cocktails loaded')"
```

## Raspberry Pi Deployment

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv
```

### 2. Auto-start on Boot

Create systemd service `/etc/systemd/system/cocktailmixer.service`:

```ini
[Unit]
Description=CocktailMixer Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/CocktailMixer/backend
Environment="PATH=/home/pi/CocktailMixer/backend/venv/bin"
ExecStart=/home/pi/CocktailMixer/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable cocktailmixer
sudo systemctl start cocktailmixer
sudo systemctl status cocktailmixer
```

## Troubleshooting

### Arduino Not Connecting
- Check port: `ls /dev/tty*` (Linux) or Device Manager (Windows)
- Verify baudrate matches Arduino sketch (9600)
- Check permissions: `sudo usermod -a -G dialout $USER` (then logout/login)

### Pumps Not Working
- Test Arduino independently with Serial Monitor
- Check relay connections
- Verify pin assignments in `config.yaml`

### YAML Parsing Errors
- Validate YAML syntax: `python -c "import yaml; yaml.safe_load(open('../db/cocktails.yaml'))"`
- Check indentation (use spaces, not tabs)

## License

MIT
