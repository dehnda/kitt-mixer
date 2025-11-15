export interface Ingredient {
    ingredient: string;
    amount: number;
    unit: string;
}

export interface Liquid {
    id: number;
    name: string;
}

export interface Cocktail {
    name: string;
    timing?: string;
    taste?: string;
    ingredients: Ingredient[];
    preparation?: string;
    is_available?: boolean;
    can_make?: boolean;  // Alias for is_available
    missing_ingredients?: string[];
}

export interface SystemStatus {
    arduino_connected: boolean;
    is_mixing: boolean;
    current_cocktail: string | null;
    progress: number;
    pumps: PumpStatus[];
}

export interface PumpStatus {
    id: number;
    pin: number;
    liquid: string | null;
    liquid_id?: number | null;
    ml_per_second: number;
    is_active: boolean;
}

export interface MakeCocktailRequest {
    size_ml: number;
}
