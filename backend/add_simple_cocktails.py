#!/usr/bin/env python3
"""
Script to add cocktails using available liquids:
- Vodka, Gin, Lemon juice, Orange juice, Cranberry juice
- Plus other common mixers if available
"""
import sys
from database.db_manager import DatabaseManager

def add_simple_cocktails(db_path: str):
    """Add cocktails using available liquids"""
    db = DatabaseManager(db_path)
    
    # Check which cocktails already exist
    existing = db.execute_query("SELECT name FROM cocktails")
    existing_names = {c['name'].lower() for c in existing}
    
    # Get liquid name to ID mapping
    liquids = db.get_all_liquids()
    liquid_map = {l['name'].lower(): l['id'] for l in liquids}
    
    print("🔍 Available liquids:")
    available = ['vodka', 'gin', 'lemon juice', 'orange juice', 'cranberry juice', 
                 'lime juice', 'simple syrup', 'soda water', 'triple sec', 'dry vermouth',
                 'sweet vermouth', 'tonic water', 'grenadine']
    for liquid in available:
        if liquid in liquid_map:
            print(f"   ✅ {liquid.title()} (ID: {liquid_map[liquid]})")
    print()
    
    # Define cocktails using only available liquids
    new_cocktails = [
        {
            'name': 'Vodka Cranberry (Cape Codder)',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Lime wedge',
            'description': 'Simple and refreshing vodka and cranberry juice',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Cranberry juice', 'amount': 12, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Vodka Orange (Screwdriver)',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Orange slice',
            'description': 'Classic vodka and orange juice cocktail',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Orange juice', 'amount': 15, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Sea Breeze',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Lime wedge',
            'description': 'Vodka with cranberry and grapefruit juice',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 4, 'unit': 'cl'},
                {'liquid': 'Cranberry juice', 'amount': 10, 'unit': 'cl'},
                {'liquid': 'Orange juice', 'amount': 6, 'unit': 'cl'},  # Using orange as substitute for grapefruit
            ]
        },
        {
            'name': 'Madras',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Lime wedge',
            'description': 'Vodka with cranberry and orange juice',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 4.5, 'unit': 'cl'},
                {'liquid': 'Cranberry juice', 'amount': 9, 'unit': 'cl'},
                {'liquid': 'Orange juice', 'amount': 9, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Vodka Lemon Drop',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Shake',
            'glass_type': 'Martini glass',
            'garnish': 'Lemon twist',
            'description': 'Sweet and sour vodka cocktail',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Lemon juice', 'amount': 2, 'unit': 'cl'},
                {'liquid': 'Simple syrup', 'amount': 1.5, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Orange Crush',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Shake',
            'glass_type': 'Highball',
            'garnish': 'Orange wedge',
            'description': 'Refreshing citrus vodka drink',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Orange juice', 'amount': 12, 'unit': 'cl'},
                {'liquid': 'Soda water', 'amount': 3, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Gin and Juice',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Orange slice',
            'description': 'Gin with orange juice',
            'ingredients': [
                {'liquid': 'Gin', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Orange juice', 'amount': 15, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Orange Blossom',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Shake',
            'glass_type': 'Cocktail glass',
            'garnish': 'Orange twist',
            'description': 'Classic gin and orange juice cocktail',
            'ingredients': [
                {'liquid': 'Gin', 'amount': 6, 'unit': 'cl'},
                {'liquid': 'Orange juice', 'amount': 6, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Gin Sour',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Shake',
            'glass_type': 'Old Fashioned',
            'garnish': 'Lemon slice and cherry',
            'description': 'Gin-based sour cocktail',
            'ingredients': [
                {'liquid': 'Gin', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Lemon juice', 'amount': 2.5, 'unit': 'cl'},
                {'liquid': 'Simple syrup', 'amount': 1.5, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Kamikaze',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Shake',
            'glass_type': 'Shot or Martini',
            'garnish': 'Lime wedge',
            'description': 'Strong citrus vodka shot',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 3, 'unit': 'cl'},
                {'liquid': 'Triple Sec', 'amount': 3, 'unit': 'cl'},
                {'liquid': 'Lime juice', 'amount': 3, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Greyhound',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Grapefruit wedge',
            'description': 'Vodka with grapefruit juice',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Orange juice', 'amount': 15, 'unit': 'cl'},  # Using orange as substitute
            ]
        },
        {
            'name': 'Harvey Wallbanger',
            'timing': 'All day',
            'taste': 'Sweet',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Orange slice and cherry',
            'description': 'Vodka, orange juice, and Galliano',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 4.5, 'unit': 'cl'},
                {'liquid': 'Orange juice', 'amount': 15, 'unit': 'cl'},
                {'liquid': 'Galliano', 'amount': 1.5, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Woo Woo',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Shake',
            'glass_type': 'Highball',
            'garnish': 'Lime wedge',
            'description': 'Vodka with cranberry and peach schnapps',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 4, 'unit': 'cl'},
                {'liquid': 'Cranberry juice', 'amount': 12, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Vodka Sunrise',
            'timing': 'All day',
            'taste': 'Sweet',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Orange slice and cherry',
            'description': 'Vodka with orange juice and grenadine',
            'ingredients': [
                {'liquid': 'Vodka', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Orange juice', 'amount': 15, 'unit': 'cl'},
                {'liquid': 'Grenadine', 'amount': 1.5, 'unit': 'cl'},
            ]
        },
        {
            'name': 'Gin Rickey',
            'timing': 'All day',
            'taste': 'Fresh',
            'preparation': 'Build',
            'glass_type': 'Highball',
            'garnish': 'Lime wedge',
            'description': 'Gin with lime juice and soda water',
            'ingredients': [
                {'liquid': 'Gin', 'amount': 5, 'unit': 'cl'},
                {'liquid': 'Lime juice', 'amount': 2, 'unit': 'cl'},
                {'liquid': 'Soda water', 'amount': 10, 'unit': 'cl'},
            ]
        },
    ]
    
    added_count = 0
    skipped_count = 0
    missing_ingredients = 0
    
    for cocktail in new_cocktails:
        name = cocktail['name']
        
        # Check if cocktail already exists
        if name.lower() in existing_names:
            print(f"⏭️  Skipping '{name}' - already exists")
            skipped_count += 1
            continue
        
        # Check if all ingredients are available
        all_ingredients_available = True
        missing = []
        for ingredient in cocktail['ingredients']:
            liquid_name = ingredient['liquid']
            if liquid_name.lower() not in liquid_map:
                all_ingredients_available = False
                missing.append(liquid_name)
        
        if not all_ingredients_available:
            print(f"⚠️  Skipping '{name}' - missing: {', '.join(missing)}")
            missing_ingredients += 1
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
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Added: {added_count} cocktails")
    print(f"   ⏭️  Skipped (already exist): {skipped_count}")
    print(f"   ⚠️  Skipped (missing ingredients): {missing_ingredients}")
    
    return added_count


if __name__ == '__main__':
    db_path = 'database/cocktails.db'
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print(f"🍸 Adding simple cocktails to database: {db_path}\n")
    add_simple_cocktails(db_path)
    print("\n✨ Done!")
