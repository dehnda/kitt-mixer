from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path

from services import DatabaseService, MixerService
from services.gpio_controller import GPIOController
from api import pumps, cocktails, status, liquids


# Global service instances
db_service: DatabaseService = None
gpio_controller: GPIOController = None
mixer_service: MixerService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global db_service, gpio_controller, mixer_service

    # Startup
    print("Starting CocktailMixer Backend...")

    # Initialize services
    db_path = os.getenv("DB_PATH", "./database/cocktails.db")

    db_service = DatabaseService(db_path)

    # Load initial data
    db_service.load_cocktails()

    # Initialize GPIO Controller
    gpio_controller = GPIOController()

    # Try to connect to GPIO (non-blocking)
    try:
        gpio_controller.connect()
        if gpio_controller.is_connected:
            print("GPIO Controller connected successfully")
        else:
            print("Warning: GPIO Controller not available (likely not on Raspberry Pi)")
            print("API will still work in simulation mode")
    except Exception as e:
        print(f"Warning: Could not connect to GPIO: {e}")
        print("API will still work in simulation mode")

    # Initialize mixer service
    mixer_service = MixerService(db_service, gpio_controller)

    print("Backend started successfully!")

    yield

    # Shutdown
    print("Shutting down CocktailMixer Backend...")

    # Ensure all pumps are stopped
    if gpio_controller and gpio_controller.is_connected:
        gpio_controller.stop_all_pumps()
        gpio_controller.disconnect()

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


def get_gpio_controller():
    return gpio_controller


def get_mixer_service():
    return mixer_service


# Update routers to use dependency injection
pumps.get_pumps.__defaults__ = (Depends(get_db_service),)
pumps.get_pump.__defaults__ = (None, Depends(get_db_service))
pumps.update_pump.__defaults__ = (None, None, Depends(get_db_service))
pumps.update_pump_liquid.__defaults__ = (None, None, Depends(get_db_service))
pumps.test_pump.__defaults__ = (None, None, Depends(get_db_service), Depends(get_gpio_controller))
pumps.stop_pump.__defaults__ = (None, Depends(get_db_service), Depends(get_gpio_controller))
pumps.stop_all_pumps.__defaults__ = (Depends(get_gpio_controller),)
pumps.test_all_pumps.__defaults__ = (None, Depends(get_db_service), Depends(get_gpio_controller))
pumps.purge_all_pumps.__defaults__ = (None, Depends(get_db_service), Depends(get_gpio_controller))

cocktails.get_all_cocktails.__defaults__ = (Depends(get_mixer_service),)
cocktails.get_available_cocktails.__defaults__ = (Depends(get_mixer_service),)
cocktails.get_cocktail.__defaults__ = (None, Depends(get_db_service))
cocktails.make_cocktail.__defaults__ = (None, None, Depends(get_mixer_service))

status.get_status.__defaults__ = (Depends(get_mixer_service), Depends(get_db_service), Depends(get_gpio_controller))
status.cancel_mixing.__defaults__ = (Depends(get_mixer_service),)
status.emergency_stop.__defaults__ = (Depends(get_mixer_service),)
status.get_diagnostics.__defaults__ = (Depends(get_db_service), Depends(get_gpio_controller))

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
        "gpio_connected": gpio_controller.is_connected if gpio_controller else False,
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
