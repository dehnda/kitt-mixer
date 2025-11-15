from typing import List, Optional
from database.db_manager import DatabaseManager


class DatabaseService:
    """Service for reading cocktails and managing pump configuration using SQLite"""

    def __init__(self, db_path: str):
        self.db = DatabaseManager(db_path)
        self._cocktails_cache = None

    def load_cocktails(self) -> List[dict]:
        """Load all cocktails from database"""
        self._cocktails_cache = self.db.get_all_cocktails()
        return self._cocktails_cache

    def get_cocktails(self) -> List[dict]:
        """Get all cocktails (use cache if available)"""
        if self._cocktails_cache is None:
            return self.load_cocktails()
        return self._cocktails_cache

    def get_cocktail_by_name(self, name: str) -> Optional[dict]:
        """Get a specific cocktail by name"""
        return self.db.get_cocktail_by_name(name)

    def get_all_unique_ingredients(self) -> List[str]:
        """Get all unique ingredients (liquid names) sorted"""
        liquids = self.db.get_all_liquids()
        return [liquid['name'] for liquid in liquids]

    def get_liquid_id_map(self) -> dict:
        """Get mapping of liquid names to IDs (lowercase name -> id)"""
        liquids = self.db.get_all_liquids()
        return {liquid['name'].lower(): liquid['id'] for liquid in liquids}

    def get_liquid_by_id(self, liquid_id: int) -> Optional[str]:
        """Get liquid name by ID"""
        liquid = self.db.get_liquid_by_id(liquid_id)
        return liquid['name'] if liquid else None

    def get_all_liquids_with_ids(self) -> List[dict]:
        """Get all unique liquids with their IDs"""
        return self.db.get_all_liquids()

    def get_id_for_liquid(self, liquid_name: str) -> Optional[int]:
        """Get ID for a liquid name (case-insensitive)"""
        liquid = self.db.get_liquid_by_name(liquid_name)
        return liquid['id'] if liquid else None

    def get_pumps(self) -> List[dict]:
        """Get all pump configurations"""
        return self.db.get_all_pumps()

    def get_pump_by_id(self, pump_id: int) -> Optional[dict]:
        """Get a specific pump by ID"""
        return self.db.get_pump_by_id(pump_id)

    def update_pump_liquid(self, pump_id: int, liquid_id: Optional[int]) -> bool:
        """Update the liquid assigned to a pump"""
        success = self.db.update_pump_liquid(pump_id, liquid_id)

        if success and liquid_id:
            # Auto-apply saved flow rate from latest calibration
            calibration = self.db.get_latest_calibration(liquid_id)
            if calibration:
                self.db.update_pump_flow_rate(pump_id, calibration['ml_per_second'])

        return success

    def update_pump_flow_rate(self, pump_id: int, ml_per_second: float) -> bool:
        """Update the flow rate (ml/sec) for a pump and save as calibration"""
        success = self.db.update_pump_flow_rate(pump_id, ml_per_second)

        if success:
            # Get pump to find liquid
            pump = self.db.get_pump_by_id(pump_id)
            if pump and pump.get('liquid_id'):
                # Record calibration
                self.db.add_calibration(
                    liquid_id=pump['liquid_id'],
                    ml_per_second=ml_per_second,
                    test_duration=10.0,  # Default
                    measured_volume=ml_per_second * 10.0,
                    notes="Flow rate update"
                )

        return success

    def get_liquid_flow_rate(self, liquid_id: int) -> Optional[float]:
        """Get the saved flow rate for a specific liquid"""
        calibration = self.db.get_latest_calibration(liquid_id)
        return calibration['ml_per_second'] if calibration else None

    def get_installed_liquids(self) -> List[str]:
        """Get list of liquids currently installed in pumps"""
        liquids = self.db.get_installed_liquids()
        return [liquid['name'] for liquid in liquids]

    def get_installed_liquid_ids(self) -> List[int]:
        """Get list of liquid IDs currently installed in pumps"""
        return self.db.get_installed_liquid_ids()

    def get_installed_liquids_with_ids(self) -> List[dict]:
        """Get installed liquids with their IDs"""
        return self.db.get_installed_liquids()

    def convert_to_ml(self, amount: float, unit: str) -> float:
        """Convert ingredient amount to milliliters"""
        cl_to_ml_str = self.db.get_setting('cl_to_ml', '10')
        cl_to_ml = float(cl_to_ml_str) if cl_to_ml_str else 10.0

        unit_lower = unit.lower()
        if unit_lower == 'cl':
            return amount * cl_to_ml
        elif unit_lower == 'ml':
            return amount
        elif unit_lower in ['dash', 'dashes']:
            return 2.0  # Approximate: 1 dash ≈ 2ml
        elif unit_lower == 'splash':
            return 5.0  # Approximate: 1 splash ≈ 5ml
        else:
            return amount  # Default fallback
