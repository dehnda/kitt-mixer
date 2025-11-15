import sqlite3
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connection and operations"""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_database()

    def _ensure_database(self):
        """Create database and tables if they don't exist"""
        schema_path = Path(__file__).parent / "schema.sql"

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Read and execute schema
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    schema = f.read()
                cursor.executescript(schema)

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT query and return the last inserted row ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid

    # ===== LIQUIDS =====

    def get_all_liquids(self) -> List[Dict[str, Any]]:
        """Get all liquids ordered by name"""
        query = "SELECT id, name, category FROM liquids ORDER BY name"
        return self.execute_query(query)

    def get_liquid_by_id(self, liquid_id: int) -> Optional[Dict[str, Any]]:
        """Get a liquid by ID"""
        query = "SELECT id, name, category FROM liquids WHERE id = ?"
        results = self.execute_query(query, (liquid_id,))
        return results[0] if results else None

    def get_liquid_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a liquid by name (case-insensitive)"""
        query = "SELECT id, name, category FROM liquids WHERE LOWER(name) = LOWER(?)"
        results = self.execute_query(query, (name,))
        return results[0] if results else None

    def add_liquid(self, name: str, category: Optional[str] = None) -> int:
        """Add a new liquid and return its ID"""
        query = "INSERT INTO liquids (name, category) VALUES (?, ?)"
        return self.execute_insert(query, (name, category))

    def get_or_create_liquid(self, name: str, category: Optional[str] = None) -> int:
        """Get liquid ID by name, or create if doesn't exist"""
        liquid = self.get_liquid_by_name(name)
        if liquid:
            return liquid['id']
        return self.add_liquid(name, category)

    # ===== PUMPS =====

    def get_all_pumps(self) -> List[Dict[str, Any]]:
        """Get all pumps with liquid information"""
        query = """
            SELECT p.id, p.pin, p.liquid_id, l.name as liquid, p.ml_per_second, p.is_active
            FROM pumps p
            LEFT JOIN liquids l ON p.liquid_id = l.id
            ORDER BY p.id
        """
        return self.execute_query(query)

    def get_pump_by_id(self, pump_id: int) -> Optional[Dict[str, Any]]:
        """Get a pump by ID with liquid information"""
        query = """
            SELECT p.id, p.pin, p.liquid_id, l.name as liquid, p.ml_per_second, p.is_active
            FROM pumps p
            LEFT JOIN liquids l ON p.liquid_id = l.id
            WHERE p.id = ?
        """
        results = self.execute_query(query, (pump_id,))
        return results[0] if results else None

    def update_pump_liquid(self, pump_id: int, liquid_id: Optional[int]) -> bool:
        """Update pump's assigned liquid"""
        query = "UPDATE pumps SET liquid_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        rows = self.execute_update(query, (liquid_id, pump_id))
        return rows > 0

    def update_pump_flow_rate(self, pump_id: int, ml_per_second: float) -> bool:
        """Update pump's flow rate"""
        query = "UPDATE pumps SET ml_per_second = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        rows = self.execute_update(query, (ml_per_second, pump_id))
        return rows > 0

    def get_installed_liquids(self) -> List[Dict[str, Any]]:
        """Get all liquids currently installed in pumps"""
        query = """
            SELECT DISTINCT l.id, l.name, l.category
            FROM pumps p
            JOIN liquids l ON p.liquid_id = l.id
            WHERE p.liquid_id IS NOT NULL AND p.is_active = 1
            ORDER BY l.name
        """
        return self.execute_query(query)

    def get_installed_liquid_ids(self) -> List[int]:
        """Get IDs of liquids currently installed in active pumps"""
        query = """
            SELECT DISTINCT liquid_id
            FROM pumps
            WHERE liquid_id IS NOT NULL AND is_active = 1
        """
        results = self.execute_query(query)
        return [row['liquid_id'] for row in results]

    # ===== COCKTAILS =====

    def get_all_cocktails(self) -> List[Dict[str, Any]]:
        """Get all cocktails with their ingredients"""
        query = "SELECT id, name, timing, taste, preparation, glass_type, garnish, description FROM cocktails ORDER BY name"
        cocktails = self.execute_query(query)

        for cocktail in cocktails:
            cocktail['ingredients'] = self.get_cocktail_ingredients(cocktail['id'])

        return cocktails

    def get_cocktail_by_id(self, cocktail_id: int) -> Optional[Dict[str, Any]]:
        """Get a cocktail by ID with ingredients"""
        query = "SELECT id, name, timing, taste, preparation, glass_type, garnish, description FROM cocktails WHERE id = ?"
        results = self.execute_query(query, (cocktail_id,))

        if not results:
            return None

        cocktail = results[0]
        cocktail['ingredients'] = self.get_cocktail_ingredients(cocktail_id)
        return cocktail

    def get_cocktail_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a cocktail by name (case-insensitive) with ingredients"""
        query = "SELECT id, name, timing, taste, preparation, glass_type, garnish, description FROM cocktails WHERE LOWER(name) = LOWER(?)"
        results = self.execute_query(query, (name,))

        if not results:
            return None

        cocktail = results[0]
        cocktail['ingredients'] = self.get_cocktail_ingredients(cocktail['id'])
        return cocktail

    def get_cocktail_ingredients(self, cocktail_id: int) -> List[Dict[str, Any]]:
        """Get all ingredients for a cocktail"""
        query = """
            SELECT l.name as ingredient, ci.amount, ci.unit, ci.is_optional, ci.liquid_id
            FROM cocktail_ingredients ci
            JOIN liquids l ON ci.liquid_id = l.id
            WHERE ci.cocktail_id = ?
            ORDER BY ci.id
        """
        return self.execute_query(query, (cocktail_id,))

    def add_cocktail(self, name: str, timing: Optional[str] = None, taste: Optional[str] = None,
                    preparation: Optional[str] = None, glass_type: Optional[str] = None,
                    garnish: Optional[str] = None, description: Optional[str] = None) -> int:
        """Add a new cocktail and return its ID"""
        query = """
            INSERT INTO cocktails (name, timing, taste, preparation, glass_type, garnish, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (name, timing, taste, preparation, glass_type, garnish, description))

    def add_cocktail_ingredient(self, cocktail_id: int, liquid_id: int, amount: float,
                               unit: str, is_optional: bool = False) -> int:
        """Add an ingredient to a cocktail"""
        query = """
            INSERT INTO cocktail_ingredients (cocktail_id, liquid_id, amount, unit, is_optional)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (cocktail_id, liquid_id, amount, unit, is_optional))

    # ===== CALIBRATIONS =====

    def add_calibration(self, liquid_id: int, ml_per_second: float, test_duration: float,
                       measured_volume: float, notes: Optional[str] = None) -> int:
        """Record a calibration test"""
        query = """
            INSERT INTO calibrations (liquid_id, ml_per_second, test_duration_seconds, measured_volume_ml, notes)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_insert(query, (liquid_id, ml_per_second, test_duration, measured_volume, notes))

    def get_latest_calibration(self, liquid_id: int) -> Optional[Dict[str, Any]]:
        """Get the most recent calibration for a liquid"""
        query = """
            SELECT id, liquid_id, ml_per_second, test_duration_seconds, measured_volume_ml, notes, created_at
            FROM calibrations
            WHERE liquid_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        """
        results = self.execute_query(query, (liquid_id,))
        return results[0] if results else None

    # ===== SETTINGS =====

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a setting value"""
        query = "SELECT value FROM settings WHERE key = ?"
        results = self.execute_query(query, (key,))
        return results[0]['value'] if results else default

    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value"""
        query = "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)"
        rows = self.execute_update(query, (key, value))
        return rows > 0

    # ===== MIX HISTORY =====

    def add_mix_history(self, cocktail_id: int, size_multiplier: float = 1.0) -> int:
        """Record the start of mixing a cocktail"""
        query = """
            INSERT INTO mix_history (cocktail_id, status, size_multiplier)
            VALUES (?, 'started', ?)
        """
        return self.execute_insert(query, (cocktail_id, size_multiplier))

    def update_mix_history_status(self, history_id: int, status: str, error_message: Optional[str] = None) -> bool:
        """Update mix history status"""
        query = """
            UPDATE mix_history
            SET status = ?, error_message = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        rows = self.execute_update(query, (status, error_message, history_id))
        return rows > 0
