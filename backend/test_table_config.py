#!/usr/bin/env python3
"""Test script for the dynamic table configuration"""

from website.jennas_amazon_products import infant_bath_tubs, infant_laundry_detergents, InfantProduct

def create_table_config(products: list, title: str, field_labels: dict = None) -> dict:
    """
    Dynamically create table configuration by analyzing which fields have actual data.
    Only includes columns where at least one product has a non-None, non-empty value.
    """
    if not products:
        return {"title": title, "columns": [], "products": []}
    
    # Default field labels - can be overridden
    default_labels = {
        "product_url": "Product",
        "name": "Product", 
        "title": "Product",
        "age_range": "Age Range",
        "material": "Material",
        "materials": "Materials",
        "comfort_support": "Comfort & Support", 
        "comfort": "Comfort",
        "cleaning": "Cleaning",
        "cleaning_effectiveness": "Cleaning",
        "storage": "Storage",
        "safety": "Safety",
        "price_range": "Price Range",
        "biggest_positive": "Pros",
        "biggest_negative": "Cons",
        "fragrance": "Fragrance",
        "ease_of_use": "Ease of Use",
        "author": "Author",
        "content_quality": "Content Quality",
        "ease_of_understanding": "Ease of Understanding",
        "evidence_based": "Evidence Based",
        "sanitization": "Sanitization",
        "drying_effectiveness": "Drying",
        "adjustability": "Adjustability",
        "material_safety": "Material Safety",
        "portability": "Portability",
        "ease_of_install": "Installation",
        "weight": "Weight",
        "purpose": "Purpose",
        "effectiveness": "Effectiveness"
    }
    
    if field_labels:
        default_labels.update(field_labels)
    
    # Get all possible fields from the first product
    sample_product = products[0]
    if hasattr(sample_product, '__dict__'):
        all_fields = list(sample_product.__dict__.keys())
    else:
        all_fields = list(sample_product.keys())
    
    # Find fields that have at least one non-None, non-empty value
    useful_fields = []
    for field in all_fields:
        if field in ['reference_url', 'amazon_url']:  # Skip these fields
            continue
            
        has_data = False
        for product in products:
            if hasattr(product, field):
                value = getattr(product, field)
            else:
                value = product.get(field)
                
            if value is not None and str(value).strip() and str(value).strip().lower() != 'n/a':
                has_data = True
                break
        
        if has_data:
            useful_fields.append(field)
    
    # Create column configurations
    columns = []
    for field in useful_fields:
        column = {
            "field": field,
            "label": default_labels.get(field, field.replace('_', ' ').title()),
            "is_link": field in ['product_url', 'name', 'title']
        }
        columns.append(column)
    
    return {
        "title": title,
        "columns": columns,
        "products": products
    }

def test_configurations():
    # Test bath tubs
    bath_tubs_objects = [InfantProduct(**item) for item in infant_bath_tubs]
    bath_config = create_table_config(bath_tubs_objects, "Infant Bath Tubs")
    
    print("=== Bath Tubs Configuration ===")
    print(f"Title: {bath_config['title']}")
    print(f"Number of products: {len(bath_config['products'])}")
    print("Columns that will be shown:")
    for col in bath_config['columns']:
        print(f"  - {col['field']}: '{col['label']}' (link: {col['is_link']})")
    
    # Test laundry detergents  
    detergent_objects = [InfantProduct(**item) for item in infant_laundry_detergents]
    detergent_config = create_table_config(detergent_objects, "Baby Laundry Detergents")
    
    print("\n=== Laundry Detergents Configuration ===")
    print(f"Title: {detergent_config['title']}")
    print(f"Number of products: {len(detergent_config['products'])}")
    print("Columns that will be shown:")
    for col in detergent_config['columns']:
        print(f"  - {col['field']}: '{col['label']}' (link: {col['is_link']})")

if __name__ == "__main__":
    test_configurations()