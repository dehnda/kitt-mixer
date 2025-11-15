from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path

from services import DatabaseService, ArduinoService, MixerService
from api import pumps, cocktails, status, liquids


# Global service instances
db_service: DatabaseService = None
arduino_service: ArduinoService = None
mixer_service: MixerService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global db_service, arduino_service, mixer_service

    # Startup
    print("Starting CocktailMixer Backend...")

    # Initialize services
    db_path = os.getenv("DB_PATH", "./database/cocktails.db")

    db_service = DatabaseService(db_path)

    # Load initial data
    db_service.load_cocktails()

    # Initialize Arduino service - get settings from database
    arduino_port = os.getenv("ARDUINO_PORT") or db_service.db.get_setting('arduino_port', 'COM3')
    arduino_baudrate = int(os.getenv("ARDUINO_BAUDRATE") or db_service.db.get_setting('arduino_baudrate', '9600'))

    arduino_service = ArduinoService(arduino_port, arduino_baudrate)

    # Try to connect to Arduino (non-blocking)
    try:
        arduino_service.connect()
    except Exception as e:
        print(f"Warning: Could not connect to Arduino: {e}")
        print("API will still work, but pump control will not be available")

    # Initialize mixer service
    mixer_service = MixerService(db_service, arduino_service)

    print("Backend started successfully!")

    yield

    # Shutdown
    print("Shutting down CocktailMixer Backend...")

    # Ensure all pumps are stopped
    if arduino_service and arduino_service.is_connected:
        arduino_service.stop_all_pumps()
        arduino_service.disconnect()

    print("Backend stopped.")


# Create FastAPI app
app = FastAPI(
    title="CocktailMixer API",
    description="API for controlling the CocktailMixer machine",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection
def get_db_service():
    return db_service


def get_arduino_service():
    return arduino_service


def get_mixer_service():
    return mixer_service


# Update routers to use dependency injection
pumps.get_pumps.__defaults__ = (Depends(get_db_service),)
pumps.get_pump.__defaults__ = (None, Depends(get_db_service))
pumps.update_pump.__defaults__ = (None, None, Depends(get_db_service))
pumps.update_pump_liquid.__defaults__ = (None, None, Depends(get_db_service))
pumps.test_pump.__defaults__ = (None, None, Depends(get_db_service), Depends(get_arduino_service))

cocktails.get_all_cocktails.__defaults__ = (Depends(get_mixer_service),)
cocktails.get_available_cocktails.__defaults__ = (Depends(get_mixer_service),)
cocktails.get_cocktail.__defaults__ = (None, Depends(get_db_service))
cocktails.make_cocktail.__defaults__ = (None, None, Depends(get_mixer_service))

status.get_status.__defaults__ = (Depends(get_mixer_service), Depends(get_db_service), Depends(get_arduino_service))
status.cancel_mixing.__defaults__ = (Depends(get_mixer_service),)
status.emergency_stop.__defaults__ = (Depends(get_mixer_service),)
status.get_diagnostics.__defaults__ = (Depends(get_db_service), Depends(get_arduino_service))

liquids.get_all_liquids.__defaults__ = (Depends(get_db_service),)
liquids.get_installed_liquids.__defaults__ = (Depends(get_db_service),)


# Include routers
app.include_router(pumps.router, prefix="/api/v1")
app.include_router(cocktails.router, prefix="/api/v1")
app.include_router(status.router, prefix="/api/v1")
app.include_router(liquids.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CocktailMixer API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "arduino_connected": arduino_service.is_connected if arduino_service else False,
        "mixer_state": mixer_service.state.value if mixer_service else "unknown"
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
