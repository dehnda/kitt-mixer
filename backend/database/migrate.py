"""
Migration script to convert YAML data to SQLite database
"""
import sys
import yaml
from pathlib import Path
from db_manager import DatabaseManager

def migrate_data(db_path: str, cocktails_yaml: str, config_yaml: str):
    """Migrate data from YAML files to SQLite database"""

    db = DatabaseManager(db_path)

    print("Starting migration...")

    # Load YAML files
    with open(cocktails_yaml, 'r', encoding='utf-8') as f:
        cocktails_data = yaml.safe_load(f)

    with open(config_yaml, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    # Migrate liquids from cocktails
    print("\n1. Migrating liquids...")
    liquid_ids = {}

    # Collect all unique liquids from cocktails
    for cocktail in cocktails_data:
        for ing in cocktail.get('ingredients', []):
            liquid_name = ing['ingredient']
            if liquid_name not in liquid_ids:
                liquid_id = db.get_or_create_liquid(liquid_name)
                liquid_ids[liquid_name] = liquid_id
                print(f"   - {liquid_name} (ID: {liquid_id})")

    print(f"   Total liquids: {len(liquid_ids)}")

    # Migrate cocktails
    print("\n2. Migrating cocktails...")
    for cocktail in cocktails_data:
        name = cocktail['name']

        # Check if cocktail already exists
        existing = db.get_cocktail_by_name(name)
        if existing:
            print(f"   - {name} (already exists)")
            continue

        cocktail_id = db.add_cocktail(
            name=name,
            timing=cocktail.get('timing'),
            taste=cocktail.get('taste'),
            preparation=cocktail.get('preparation')
        )

        # Add ingredients
        for ing in cocktail.get('ingredients', []):
            liquid_name = ing['ingredient']
            liquid_id = liquid_ids[liquid_name]

            db.add_cocktail_ingredient(
                cocktail_id=cocktail_id,
                liquid_id=liquid_id,
                amount=ing['amount'],
                unit=ing['unit']
            )

        print(f"   - {name} (ID: {cocktail_id}) with {len(cocktail.get('ingredients', []))} ingredients")

    # Migrate pumps
    print("\n3. Migrating pumps...")

    # First, create pump entries if they don't exist
    for pump_data in config_data.get('pumps', []):
        pump_id = pump_data['id']
        pin = pump_data['pin']

        # Check if pump exists
        existing = db.get_pump_by_id(pump_id)
        if not existing:
            # Insert pump
            query = "INSERT INTO pumps (id, pin) VALUES (?, ?)"
            db.execute_insert(query, (pump_id, pin))
            print(f"   - Created pump {pump_id} on pin {pin}")

        # Update pump configuration
        liquid_name = pump_data.get('liquid')
        liquid_id = None

        if liquid_name:
            # Get or create liquid
            liquid_id = db.get_or_create_liquid(liquid_name)

        ml_per_second = pump_data.get('ml_per_second', 10.0)

        db.update_pump_liquid(pump_id, liquid_id)
        db.update_pump_flow_rate(pump_id, ml_per_second)

        print(f"   - Pump {pump_id}: {liquid_name or 'Empty'} @ {ml_per_second} ml/s")

    # Migrate settings
    print("\n4. Migrating settings...")
    if 'conversion' in config_data:
        cl_to_ml = config_data['conversion'].get('cl_to_ml', 10)
        db.set_setting('cl_to_ml', str(cl_to_ml))
        print(f"   - cl_to_ml: {cl_to_ml}")

    if 'arduino' in config_data:
        arduino = config_data['arduino']
        db.set_setting('arduino_port', arduino.get('port', 'COM3'))
        db.set_setting('arduino_baudrate', str(arduino.get('baudrate', 9600)))
        db.set_setting('arduino_timeout', str(arduino.get('timeout', 2)))
        print(f"   - Arduino: {arduino.get('port')} @ {arduino.get('baudrate')}")

    # Migrate liquid flow rates to calibrations
    print("\n5. Migrating liquid flow rates...")
    if 'liquid_flow_rates' in config_data:
        for liquid_name, flow_rate in config_data['liquid_flow_rates'].items():
            liquid_id = db.get_or_create_liquid(liquid_name)
            db.add_calibration(
                liquid_id=liquid_id,
                ml_per_second=flow_rate,
                test_duration=10.0,  # Default
                measured_volume=flow_rate * 10.0,  # Calculated
                notes="Migrated from YAML config"
            )
            print(f"   - {liquid_name}: {flow_rate} ml/s")

    print("\n✅ Migration complete!")

    # Print summary
    print("\n📊 Database Summary:")
    all_liquids = db.get_all_liquids()
    all_cocktails = db.get_all_cocktails()
    all_pumps = db.get_all_pumps()

    print(f"   - Liquids: {len(all_liquids)}")
    print(f"   - Cocktails: {len(all_cocktails)}")
    print(f"   - Pumps: {len(all_pumps)}")

    installed = db.get_installed_liquids()
    print(f"   - Installed liquids: {len(installed)}")
    if installed:
        print(f"     {', '.join([l['name'] for l in installed])}")


if __name__ == '__main__':
    # Default paths
    project_root = Path(__file__).parent.parent.parent
    db_path = project_root / 'backend' / 'database' / 'cocktails.db'
    cocktails_yaml = project_root / 'db' / 'cocktails.yaml'
    config_yaml = project_root / 'backend' / 'config.yaml'

    print(f"Database: {db_path}")
    print(f"Cocktails YAML: {cocktails_yaml}")
    print(f"Config YAML: {config_yaml}")

    if not cocktails_yaml.exists():
        print(f"❌ Error: {cocktails_yaml} not found")
        sys.exit(1)

    if not config_yaml.exists():
        print(f"❌ Error: {config_yaml} not found")
        sys.exit(1)

    migrate_data(str(db_path), str(cocktails_yaml), str(config_yaml))
