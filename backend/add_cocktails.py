#!/usr/bin/env python3
"""
Script to add popular cocktails to the database
"""
import sys
from database.db_manager import DatabaseManager

def add_new_cocktails(db_path: str):
    """Add popular cocktails that are missing"""
    db = DatabaseManager(db_path)
    
    # Check which cocktails already exist
    existing = db.execute_query("SELECT name FROM cocktails")
    existing_names = {c['name'].lower() for c in existing}
    
    # Define new cocktails to add
    new_cocktails = [
        {
            'name': 'Mojito',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Mint sprig and lime wheel',
            'description': 'A refreshing Cuban classic with mint, lime, sugar, rum, and soda water',
            'ingredients': [
                {'liquid': 'Light Rum', 'amount': 4.5, 'unit': 'cl'},
                {'liquid': 'Lime juice', 'amount': 2, 'unit': 'cl'},
                {'liquid': 'Simple syrup', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Soda water', 'amount': 10, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Moscow Mule',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Copper mug or Highball',
            'garnish': 'Lime wheel',
            'description': 'Vodka, ginger beer, and lime juice in a copper mug',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 4.5, 'unit': 'cl'},
                {'liquid': 'Lime juice', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Soda water', 'amount': 12, 'unit': 'cl'},  # Using soda as substitute for ginger beer
            ]
        },
        {
            'name': 'Espresso Martini',
            'timing': 'After dinner',
            'taste': 'Sweet',
            'preparation': 'Shake',
            'glass_type': 'Cocktail glass',
            'garnish': 'Coffee beans',
            'description': 'Vodka shaken with fresh espresso and coffee liqueur',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Coffee', 'amount': 3, 'unit': 'cl'},
                {'liquid': 'Simple syrup', 'amount': 1, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Aperol Spritz',
            'timing': 'Pre-dinner',
            'taste': 'Bitter sweet',
            'preparation': 'Build',
            'glass_type': 'Wine glass',
            'garnish': 'Orange slice',
            'description': 'Italian aperitif with Aperol, Prosecco, and soda',
            'ingredients': [
                {'liquid': 'Aperol', 'amount': 6, 'unit': 'cl'},
                {'liquid': 'Prosecco', 'amount': 9, 'unit': 'cl'},
                {'liquid': 'Soda water', 'amount': 3, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Pina Colada',
            'timing': 'All day',
            'taste': 'Sweet',
            'preparation': 'Blend',
            'glass_type': 'Hurricane glass',
            'garnish': 'Pineapple wedge and cherry',
            'description': 'Tropical cocktail with rum, pineapple juice, and coconut cream',
            'ingredients': [
                {'liquid': 'Light Rum', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Pineapple juice', 'amount': 9, 'unit': 'cl'},
                {'liquid': 'Fresh cream', 'amount': 3, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Long Island Iced Tea',
            'timing': 'All day',
            'taste': 'Boozy',
            'preparation': 'Shake and top',
            'glass_type': 'Highball',
            'garnish': 'Lemon wedge',
            'description': 'Strong cocktail with multiple spirits',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Gin', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Light Rum', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Tequila', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Triple Sec', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Lemon juice', 'amount': 2.5, 'unit': 'cl'},
                {'liquid': 'Simple syrup', 'amount': 1.5, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Whiskey Sour',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Shake',
            'glass_type': 'Old Fashioned',
            'garnish': 'Cherry and orange slice',
            'description': 'Classic sour cocktail with whiskey, lemon, and sugar',
            'ingredients': [
                {'liquid': 'Bourbon Whiskey', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Lemon juice', 'amount': 2.5, 'unit': 'cl'},
                {'liquid': 'Simple syrup', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Egg white', 'amount': 1.5, 'unit': 'cl', 'is_optional': True},
            ]
        },
        {
            'name': 'Mai Tai',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Shake',
            'glass_type': 'Old Fashioned',
            'garnish': 'Mint sprig and lime wheel',
            'description': 'Tropical rum cocktail with orgeat and lime',
            'ingredients': [
                {'liquid': 'Light Rum', 'amount': 4, 'unit': 'cl'},
                {'liquid': 'Orange juice', 'amount': 2, 'unit': 'cl'},
                {'liquid': 'Lime juice', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Orgeat', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Triple Sec', 'amount': 1, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Bramble',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Old Fashioned',
            'garnish': 'Blackberry and lemon slice',
            'description': 'Gin cocktail with blackberry liqueur',
            'ingredients': [
                {'liquid': 'Gin', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Lemon juice', 'amount': 2.5, 'unit': 'cl'},
                {'liquid': 'Simple syrup', 'amount': 1.5, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Paloma',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Grapefruit wedge',
            'description': 'Tequila with grapefruit juice and soda',
            'ingredients': [
                {'liquid': 'Tequila', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Grapefruit juice', 'amount': 6, 'unit': 'cl'},
                {'liquid': 'Lime juice', 'amount': 1.5, 'unit': 'cl'},
                {'liquid': 'Soda water', 'amount': 6, 'unit': 'cl'},
            ]
        },
    ]
    
    # Get liquid name to ID mapping
    liquids = db.get_all_liquids()
    liquid_map = {l['name'].lower(): l['id'] for l in liquids}
    
    added_count = 0
    skipped_count = 0
    
    for cocktail in new_cocktails:
        name = cocktail['name']
        
        # Check if cocktail already exists
        if name.lower() in existing_names:
            print(f"⏭️  Skipping '{name}' - already exists")
            skipped_count += 1
            continue
        
        try:
            # Add cocktail
            cocktail_id = db.add_cocktail(
                name=name,
                timing=cocktail.get('timing'),
                taste=cocktail.get('taste'),
                preparation=cocktail.get('preparation'),
                glass_type=cocktail.get('glass_type'),
                garnish=cocktail.get('garnish'),
                description=cocktail.get('description')
            )
            
            # Add ingredients
            for ingredient in cocktail['ingredients']:
                liquid_name = ingredient['liquid']
                liquid_id = liquid_map.get(liquid_name.lower())
                
                if not liquid_id:
                    print(f"⚠️  Warning: Liquid '{liquid_name}' not found for {name}")
                    continue
                
                db.add_cocktail_ingredient(
                    cocktail_id=cocktail_id,
                    liquid_id=liquid_id,
                    amount=ingredient['amount'],
                    unit=ingredient['unit'],
                    is_optional=ingredient.get('is_optional', False)
                )
            
            print(f"✅ Added '{name}' (ID: {cocktail_id})")
            added_count += 1
            
        except Exception as e:
            print(f"❌ Error adding '{name}': {e}")
    
    print(f"\n📊 Summary: Added {added_count} cocktails, Skipped {skipped_count} existing")
    return added_count


if __name__ == '__main__':
    db_path = 'database/cocktails.db'
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print(f"🍸 Adding cocktails to database: {db_path}\n")
    add_new_cocktails(db_path)
    print("\n✨ Done!")
