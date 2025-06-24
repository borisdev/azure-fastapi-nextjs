#!/usr/bin/env python3
"""
Analyze which fields are consistently None/missing across product categories
to identify which table columns should be hidden.
"""

import json
from collections import defaultdict
from website.jennas_amazon_products import *


def analyze_category(products, category_name):
    """Analyze a product category to find consistently missing fields"""
    if not products:
        return {}
    
    print(f"\n=== {category_name.upper()} ===")
    print(f"Total products: {len(products)}")
    
    # Get all possible fields from InfantProduct model
    all_fields = [
        'product_url', 'name', 'title', 'age_range', 'material', 'comfort_support',
        'cleaning', 'cleaning_effectiveness', 'storage', 'safety', 'price_range',
        'reference_url', 'amazon_url', 'biggest_negative', 'biggest_positive',
        'fragrance', 'ease_of_use', 'author', 'content_quality', 'ease_of_understanding',
        'evidence_based', 'sanitization', 'drying_effectiveness', 'comfort',
        'adjustability', 'material_safety', 'portability', 'ease_of_install',
        'weight', 'materials', 'purpose', 'effectiveness'
    ]
    
    # Count how many products have each field
    field_counts = defaultdict(int)
    field_values = defaultdict(list)
    
    for product in products:
        for field in all_fields:
            value = product.get(field)
            if value is not None and value != "":
                field_counts[field] += 1
                field_values[field].append(value)
    
    # Identify fields that are present vs missing
    total_products = len(products)
    present_fields = []
    missing_fields = []
    
    for field in all_fields:
        count = field_counts[field]
        if count == 0:
            missing_fields.append(field)
        else:
            present_fields.append((field, count, count/total_products))
    
    print("\nFields PRESENT in this category:")
    for field, count, percentage in sorted(present_fields, key=lambda x: x[1], reverse=True):
        print(f"  {field}: {count}/{total_products} ({percentage:.1%})")
    
    print(f"\nFields ALWAYS MISSING (should be hidden): {len(missing_fields)}")
    for field in sorted(missing_fields):
        print(f"  {field}")
    
    return {
        'category': category_name,
        'total_products': total_products,
        'present_fields': present_fields,
        'missing_fields': missing_fields
    }


def main():
    """Analyze all product categories"""
    categories = [
        (infant_bath_tubs, "infant_bath_tubs"),
        (infant_laundry_detergents, "infant_laundry_detergents"),
        (infant_care_books, "infant_care_books"),
        (bottle_cleaners, "bottle_cleaners"),
        (bottle_sanitizers, "bottle_sanitizers"),
        (bottle_dryers, "bottle_dryers"),
        (infant_high_chairs, "infant_high_chairs"),
        (infant_nursing_pillows, "infant_nursing_pillows"),
        (non_toxic_playmats, "non_toxic_playmats"),
        (baby_carrier_wraps, "baby_carrier_wraps"),
        (post_delivery_healing_products, "post_delivery_healing_products"),
        (non_toxic_infant_car_seats, "non_toxic_infant_car_seats"),
        (non_toxic_bassinets, "non_toxic_bassinets"),
    ]
    
    all_results = []
    
    for products, category_name in categories:
        result = analyze_category(products, category_name)
        all_results.append(result)
    
    # Summary analysis
    print("\n" + "="*60)
    print("SUMMARY: Fields that are ALWAYS missing across ALL categories")
    print("="*60)
    
    # Find fields that are missing in ALL categories
    all_missing_fields = set()
    category_missing_fields = {}
    
    for result in all_results:
        category_missing_fields[result['category']] = set(result['missing_fields'])
        if not all_missing_fields:
            all_missing_fields = set(result['missing_fields'])
        else:
            all_missing_fields &= set(result['missing_fields'])
    
    print(f"\nFields missing in ALL {len(all_results)} categories (safe to hide globally):")
    for field in sorted(all_missing_fields):
        print(f"  {field}")
    
    # Show category-specific missing fields
    print(f"\nCategory-specific missing fields:")
    for category, missing in category_missing_fields.items():
        category_specific = missing - all_missing_fields
        if category_specific:
            print(f"  {category}: {sorted(category_specific)}")


if __name__ == "__main__":
    main()