#!/usr/bin/env python3
"""Test the complete dynamic table system"""

import sys
sys.path.append('.')

from website.jennas_amazon_products import infant_bath_tubs, infant_laundry_detergents, InfantProduct
from website.main import create_table_config

def test_dynamic_tables():
    print("=== Testing Dynamic Table System ===\n")
    
    # Test bath tubs
    bath_tubs_objects = [InfantProduct(**item) for item in infant_bath_tubs]
    bath_config = create_table_config(bath_tubs_objects, "Infant Bath Tubs")
    
    print(f"Bath Tubs Table:")
    print(f"  Title: {bath_config['title']}")
    print(f"  Columns: {len(bath_config['columns'])}")
    for col in bath_config['columns']:
        print(f"    - {col['label']} (field: {col['field']}, link: {col['is_link']})")
    
    print(f"  Products: {len(bath_config['products'])}")
    if bath_config['products']:
        sample_product = bath_config['products'][0]
        print(f"  Sample product keys: {list(sample_product.keys())}")
        if '_link_text' in sample_product:
            print(f"  Sample link text: {sample_product['_link_text']}")
        if '_link_url' in sample_product:
            print(f"  Sample link URL: {sample_product['_link_url'][:50]}...")
    
    print("\n" + "="*60 + "\n")
    
    # Test laundry detergents
    detergent_objects = [InfantProduct(**item) for item in infant_laundry_detergents]
    detergent_config = create_table_config(detergent_objects, "Baby Laundry Detergents")
    
    print(f"Laundry Detergents Table:")
    print(f"  Title: {detergent_config['title']}")
    print(f"  Columns: {len(detergent_config['columns'])}")
    for col in detergent_config['columns']:
        print(f"    - {col['label']} (field: {col['field']}, link: {col['is_link']})")
    
    print(f"  Products: {len(detergent_config['products'])}")
    if detergent_config['products']:
        sample_product = detergent_config['products'][0]
        print(f"  Sample product keys: {list(sample_product.keys())}")
        
        # Show some sample field values
        for col in detergent_config['columns']:
            if not col['is_link'] and col['field'] in sample_product:
                value = sample_product[col['field']]
                print(f"    {col['field']}: {value[:30]}..." if len(str(value)) > 30 else f"    {col['field']}: {value}")
    
    print("\n=== Test Completed Successfully ===")

if __name__ == "__main__":
    test_dynamic_tables()