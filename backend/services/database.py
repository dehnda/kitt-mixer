import yaml
import os
from typing import List, Optional
from pathlib import Path


class DatabaseService:
    """Service for reading cocktails and managing pump configuration"""

    def __init__(self, cocktails_path: str, config_path: str):
        self.cocktails_path = Path(cocktails_path)
        self.config_path = Path(config_path)
        self._cocktails_cache = None
        self._config_cache = None

    def load_cocktails(self) -> List[dict]:
        """Load all cocktails from YAML database"""
        try:
            with open(self.cocktails_path, 'r', encoding='utf-8') as f:
                cocktails = yaml.safe_load(f)
                self._cocktails_cache = cocktails if cocktails else []
                return self._cocktails_cache
        except FileNotFoundError:
            print(f"Cocktails database not found at {self.cocktails_path}")
            return []
        except yaml.YAMLError as e:
            print(f"Error parsing cocktails YAML: {e}")
            return []

    def get_cocktails(self) -> List[dict]:
        """Get all cocktails (use cache if available)"""
        if self._cocktails_cache is None:
            return self.load_cocktails()
        return self._cocktails_cache

    def get_cocktail_by_name(self, name: str) -> Optional[dict]:
        """Get a specific cocktail by name"""
        cocktails = self.get_cocktails()
        for cocktail in cocktails:
            if cocktail.get('name', '').lower() == name.lower():
                return cocktail
        return None

    def get_all_unique_ingredients(self) -> List[str]:
        """Get all unique ingredients from all cocktails"""
        cocktails = self.get_cocktails()
        ingredients = set()
        for cocktail in cocktails:
            for ing in cocktail.get('ingredients', []):
                ingredients.add(ing['ingredient'])
        return sorted(list(ingredients))

    def load_config(self) -> dict:
        """Load configuration from YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self._config_cache = config
                return config
        except FileNotFoundError:
            print(f"Config file not found at {self.config_path}")
            return {"pumps": [], "arduino": {}, "conversion": {"cl_to_ml": 10}}
        except yaml.YAMLError as e:
            print(f"Error parsing config YAML: {e}")
            return {"pumps": [], "arduino": {}, "conversion": {"cl_to_ml": 10}}

    def get_config(self) -> dict:
        """Get configuration (use cache if available)"""
        if self._config_cache is None:
            return self.load_config()
        return self._config_cache

    def get_pumps(self) -> List[dict]:
        """Get all pump configurations"""
        config = self.get_config()
        return config.get('pumps', [])

    def get_pump_by_id(self, pump_id: int) -> Optional[dict]:
        """Get a specific pump by ID"""
        pumps = self.get_pumps()
        for pump in pumps:
            if pump.get('id') == pump_id:
                return pump
        return None

    def update_pump_liquid(self, pump_id: int, liquid: Optional[str]) -> bool:
        """Update the liquid assigned to a pump and apply saved flow rate if available"""
        config = self.get_config()
        pumps = config.get('pumps', [])

        for pump in pumps:
            if pump.get('id') == pump_id:
                pump['liquid'] = liquid
                # Auto-apply saved flow rate for this liquid if available
                if liquid:
                    liquid_flow_rates = config.get('liquid_flow_rates', {})
                    if liquid in liquid_flow_rates:
                        pump['ml_per_second'] = liquid_flow_rates[liquid]
                break
        else:
            return False

        # Save updated config
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            self._config_cache = config
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def update_pump_flow_rate(self, pump_id: int, ml_per_second: float) -> bool:
        """Update the flow rate (ml/sec) for a pump and optionally save for the liquid"""
        config = self.get_config()
        pumps = config.get('pumps', [])

        for pump in pumps:
            if pump.get('id') == pump_id:
                pump['ml_per_second'] = ml_per_second
                # Also save this flow rate for the liquid if one is assigned
                liquid = pump.get('liquid')
                if liquid:
                    if 'liquid_flow_rates' not in config:
                        config['liquid_flow_rates'] = {}
                    config['liquid_flow_rates'][liquid] = ml_per_second
                break
        else:
            return False

        # Save updated config
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            self._config_cache = config
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_liquid_flow_rate(self, liquid: str) -> Optional[float]:
        """Get the saved flow rate for a specific liquid"""
        config = self.get_config()
        liquid_flow_rates = config.get('liquid_flow_rates', {})
        return liquid_flow_rates.get(liquid)

    def get_installed_liquids(self) -> List[str]:
        """Get list of liquids currently installed in pumps"""
        pumps = self.get_pumps()
        liquids = [p['liquid'] for p in pumps if p.get('liquid') is not None]
        return liquids

    def convert_to_ml(self, amount: float, unit: str) -> float:
        """Convert ingredient amount to milliliters"""
        config = self.get_config()
        cl_to_ml = config.get('conversion', {}).get('cl_to_ml', 10)

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
