export interface Ingredient {
    ingredient: string;
    amount: number;
    unit: string;
}

export interface Cocktail {
    name: string;
    timing?: string;
    taste?: string;
    ingredients: Ingredient[];
    preparation?: string;
    can_make?: boolean;
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
    ml_per_second: number;
    is_active: boolean;
}

export interface MakeCocktailRequest {
    size_ml: number;
}
