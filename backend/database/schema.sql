-- CocktailMixer Database Schema

-- Liquids master table
CREATE TABLE IF NOT EXISTS liquids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT, -- e.g., 'spirit', 'liqueur', 'mixer', 'juice', 'syrup'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pumps configuration
CREATE TABLE IF NOT EXISTS pumps (
    id INTEGER PRIMARY KEY,
    pin INTEGER NOT NULL UNIQUE,
    liquid_id INTEGER,
    ml_per_second REAL DEFAULT 10.0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (liquid_id) REFERENCES liquids(id) ON DELETE SET NULL
);

-- Cocktails
CREATE TABLE IF NOT EXISTS cocktails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    timing TEXT, -- e.g., 'Pre-dinner', 'After dinner', 'All day'
    taste TEXT, -- e.g., 'Bitter sweet', 'Fresh', 'Sour'
    preparation TEXT, -- e.g., 'Shaken', 'Stirred', 'Built'
    glass_type TEXT,
    garnish TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cocktail ingredients (many-to-many relationship)
CREATE TABLE IF NOT EXISTS cocktail_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cocktail_id INTEGER NOT NULL,
    liquid_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    unit TEXT NOT NULL, -- e.g., 'cl', 'ml', 'dash', 'splash'
    is_optional BOOLEAN DEFAULT 0,
    FOREIGN KEY (cocktail_id) REFERENCES cocktails(id) ON DELETE CASCADE,
    FOREIGN KEY (liquid_id) REFERENCES liquids(id) ON DELETE CASCADE,
    UNIQUE(cocktail_id, liquid_id)
);

-- Liquid flow rate calibrations (history)
CREATE TABLE IF NOT EXISTS calibrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    liquid_id INTEGER NOT NULL,
    ml_per_second REAL NOT NULL,
    test_duration_seconds REAL NOT NULL,
    measured_volume_ml REAL NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (liquid_id) REFERENCES liquids(id) ON DELETE CASCADE
);

-- Mixing history/logs
CREATE TABLE IF NOT EXISTS mix_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cocktail_id INTEGER NOT NULL,
    status TEXT NOT NULL, -- 'completed', 'failed', 'cancelled'
    size_multiplier REAL DEFAULT 1.0,
    error_message TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (cocktail_id) REFERENCES cocktails(id) ON DELETE CASCADE
);

-- System settings
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_cocktail_ingredients_cocktail ON cocktail_ingredients(cocktail_id);
CREATE INDEX IF NOT EXISTS idx_cocktail_ingredients_liquid ON cocktail_ingredients(liquid_id);
CREATE INDEX IF NOT EXISTS idx_mix_history_cocktail ON mix_history(cocktail_id);
CREATE INDEX IF NOT EXISTS idx_calibrations_liquid ON calibrations(liquid_id);

-- Insert default settings
INSERT OR IGNORE INTO settings (key, value) VALUES ('cl_to_ml', '10');
INSERT OR IGNORE INTO settings (key, value) VALUES ('arduino_port', 'COM3');
INSERT OR IGNORE INTO settings (key, value) VALUES ('arduino_baudrate', '9600');
INSERT OR IGNORE INTO settings (key, value) VALUES ('arduino_timeout', '2');
