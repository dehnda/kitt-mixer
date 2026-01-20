from typing import List, Optional, Dict
from services.database import DatabaseService
from services.gpio_controller import GPIOController
from services.arduino import ArduinoService
from models import MixerState, Cocktail, CocktailWithAvailability, Ingredient
import threading
import time


class MixerService:
    """Service for mixing cocktails and managing mixer state"""

    def __init__(self, db_service: DatabaseService, controller: GPIOController, arduino_service: ArduinoService):
        self.db = db_service
        self.controller = controller  # GPIO controller
        self.arduino = arduino_service
        self.state = MixerState.IDLE
        self.current_cocktail: Optional[str] = None
        self.progress_percent: float = 0.0
        self.error_message: Optional[str] = None
        self.mixing_thread: Optional[threading.Thread] = None
        self.cancel_flag = False
        self.simulation_mode = not controller.is_connected

    def get_status(self) -> Dict:
        """Get current mixer status"""
        return {
            "state": self.state.value,
            "current_cocktail": self.current_cocktail,
            "progress_percent": self.progress_percent,
            "error_message": self.error_message
        }

    def get_available_cocktails(self) -> List[CocktailWithAvailability]:
        """Get all cocktails with availability based on installed liquids (using IDs)"""
        cocktails = self.db.get_cocktails()
        installed_liquid_ids = set(self.db.get_installed_liquid_ids())

        result = []
        for cocktail_data in cocktails:
            # Parse ingredients
            ingredients = [
                Ingredient(**ing) for ing in cocktail_data.get('ingredients', [])
            ]

            # Create cocktail object
            cocktail = Cocktail(
                name=cocktail_data['name'],
                timing=cocktail_data.get('timing'),
                taste=cocktail_data.get('taste'),
                ingredients=ingredients,
                preparation=cocktail_data.get('preparation')
            )

            # Get required liquid IDs (case-insensitive lookup)
            required_liquid_ids = set()
            ingredient_name_to_id = {}
            for ing in ingredients:
                liquid_id = self.db.get_id_for_liquid(ing.ingredient)
                if liquid_id:
                    required_liquid_ids.add(liquid_id)
                    ingredient_name_to_id[liquid_id] = ing.ingredient

            # Check availability by comparing IDs
            missing_ids = required_liquid_ids - installed_liquid_ids

            # Get original ingredient names for missing items
            missing_original = [ingredient_name_to_id[lid] for lid in missing_ids if lid in ingredient_name_to_id]

            cocktail_with_avail = CocktailWithAvailability(
                **cocktail.model_dump(),
                is_available=len(missing_ids) == 0,
                missing_ingredients=sorted(missing_original)
            )

            result.append(cocktail_with_avail)

        return result

    def get_makeable_cocktails(self) -> List[CocktailWithAvailability]:
        """Get only cocktails that can be made with current liquids"""
        all_cocktails = self.get_available_cocktails()
        return [c for c in all_cocktails if c.is_available]

    def can_make_cocktail(self, cocktail_name: str) -> tuple[bool, List[str]]:
        """
        Check if a cocktail can be made (using liquid IDs)

        Returns:
            Tuple of (can_make: bool, missing_ingredients: List[str])
        """
        cocktail_data = self.db.get_cocktail_by_name(cocktail_name)
        if not cocktail_data:
            return False, ["Cocktail not found"]

        installed_liquid_ids = set(self.db.get_installed_liquid_ids())

        # Get required liquid IDs
        required_liquid_ids = set()
        ingredient_map = {}

        for ing in cocktail_data.get('ingredients', []):
            liquid_id = self.db.get_id_for_liquid(ing['ingredient'])
            if liquid_id:
                required_liquid_ids.add(liquid_id)
                ingredient_map[liquid_id] = ing['ingredient']

        missing_ids = required_liquid_ids - installed_liquid_ids
        missing_names = [ingredient_map[lid] for lid in missing_ids if lid in ingredient_map]

        return len(missing_ids) == 0, sorted(missing_names)

    def make_cocktail(self, cocktail_name: str, size_multiplier: float = 1.0) -> bool:
        """
        Start making a cocktail (non-blocking)

        Args:
            cocktail_name: Name of the cocktail to make
            size_multiplier: Multiplier for recipe (1.0 = normal size)

        Returns:
            True if mixing started, False otherwise
        """
        if self.state != MixerState.IDLE:
            self.error_message = "Mixer is busy"
            return False

        # Check if cocktail can be made
        can_make, missing = self.can_make_cocktail(cocktail_name)
        if not can_make:
            self.error_message = f"Cannot make cocktail. Missing: {', '.join(missing)}"
            return False

        # Start mixing in background thread
        self.cancel_flag = False
        self.mixing_thread = threading.Thread(
            target=self._mix_cocktail_thread,
            args=(cocktail_name, size_multiplier)
        )
        self.mixing_thread.start()

        return True

    def _mix_cocktail_thread(self, cocktail_name: str, size_multiplier: float):
        """Background thread for mixing cocktail"""
        try:
            self.state = MixerState.MIXING
            self.current_cocktail = cocktail_name
            self.progress_percent = 0.0
            self.error_message = None

            # Indicate that mixing has started (arduino will show mixing LED)
            # self.arduino.send_command("1") # Deactivate for now because cables are a mess

            # Get cocktail recipe
            cocktail_data = self.db.get_cocktail_by_name(cocktail_name)
            if not cocktail_data:
                raise Exception("Cocktail not found")

            ingredients = cocktail_data.get('ingredients', [])
            pumps = {p['liquid']: p for p in self.db.get_pumps() if p.get('liquid')}

            # Calculate steps
            total_steps = len(ingredients)

            for idx, ingredient in enumerate(ingredients):
                if self.cancel_flag:
                    self.state = MixerState.IDLE
                    self.current_cocktail = None
                    self.progress_percent = 0.0
                    return

                liquid = ingredient['ingredient']
                amount = ingredient['amount']
                unit = ingredient['unit']

                # Update progress at start of ingredient
                self.progress_percent = (idx / total_steps) * 100

                if self.simulation_mode:
                    # Simulation mode - just wait without real hardware
                    print(f"[SIMULATION] Dispensing {amount} {unit} of {liquid}")
                    time.sleep(2)  # Simulate 2 seconds per ingredient
                else:
                    # Real mode - use GPIO controller
                    # Find pump for this liquid
                    if liquid not in pumps:
                        print(f"Warning: No pump found for {liquid}, skipping")
                        continue

                    pump = pumps[liquid]

                    # Convert to ml
                    ml = self.db.convert_to_ml(amount, unit) * size_multiplier

                    # Calculate duration
                    duration_ms = self.controller.calculate_duration_ms(ml, pump['id'])
                      # Start pump
                    print(f"Dispensing {ml}ml of {liquid} (pump {pump['id']}) for {duration_ms}ms")

                    success = self.controller.start_pump(pump['id'], duration_ms)

                    if not success:
                        raise Exception(f"Failed to start pump {pump['id']}")

                    # Wait for pump to finish (with some buffer)
                    wait_time = duration_ms / 1000.0 + 0.5
                    time.sleep(wait_time)

                # Update progress after ingredient
                self.progress_percent = ((idx + 1) / total_steps) * 100

            # Mixing complete
            self.state = MixerState.IDLE
            self.current_cocktail = None
            self.progress_percent = 100.0
            mode_str = "[SIMULATION]" if self.simulation_mode else ""
            print(f"{mode_str} Cocktail '{cocktail_name}' completed!")

            # Start mixer motor for final mixing (only in real mode)
            if not self.simulation_mode:
                print("Mixing currently disabled in real mode, because cables are a mess and need to get out of the way.")
                # print("Starting mixer motor for however it long it takes ...")
                # self.arduino.send_command("2")

        except Exception as e:
            self.state = MixerState.ERROR
            self.error_message = str(e)
            print(f"Error mixing cocktail: {e}")

            # Try to stop all pumps on error (only if not in simulation mode)
            if not self.simulation_mode:
                self.controller.stop_all_pumps()
                self.controller.stop_mixer()

    def cancel_mixing(self) -> bool:
        """Cancel current mixing operation"""
        if self.state != MixerState.MIXING:
            return False

        self.cancel_flag = True
        if not self.simulation_mode:
            self.controller.stop_all_pumps()
            self.controller.stop_mixer()

        # Wait for thread to finish
        if self.mixing_thread and self.mixing_thread.is_alive():
            self.mixing_thread.join(timeout=5)

        self.state = MixerState.IDLE
        self.current_cocktail = None
        self.progress_percent = 0.0

        return True

    def emergency_stop(self):
        """Emergency stop - immediately stop all pumps and mixer"""
        if not self.simulation_mode:
            self.controller.stop_all_pumps()
            self.controller.stop_mixer()
        self.cancel_flag = True
        self.state = MixerState.IDLE
        self.current_cocktail = None
        self.progress_percent = 0.0
