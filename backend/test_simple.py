#!/usr/bin/env python3
"""Simple test of the table configuration logic"""

from website.jennas_amazon_products import infant_bath_tubs, InfantProduct

# Test creating an enhanced product dict
def create_enhanced_product(product, columns):
    product_dict = {"_product": product}
    for column in columns:
        if column["is_link"]:
            product_dict["_link_text"] = product.display_name or product.name or product.title or "Product"
            product_dict["_link_url"] = product.product_url or "#"
        else:
            value = getattr(product, column["field"], None)
            product_dict[column["field"]] = value if value else "N/A"
    return product_dict

# Test with bath tub data
product = InfantProduct(**infant_bath_tubs[0])
print("Original product name:", product.name)
print("Original product URL:", product.product_url)

# Simulate columns for bath tubs
columns = [
    {"field": "name", "label": "Product", "is_link": True},
    {"field": "age_range", "label": "Age Range", "is_link": False},
    {"field": "material", "label": "Material", "is_link": False},
    {"field": "safety", "label": "Safety", "is_link": False},
    {"field": "price_range", "label": "Price Range", "is_link": False}
]

enhanced = create_enhanced_product(product, columns)
print("\nEnhanced product dict:")
for key, value in enhanced.items():
    if key.startswith('_'):
        print(f"  {key}: {value}")
    else:
        print(f"  {key}: {value[:50]}..." if len(str(value)) > 50 else f"  {key}: {value}")

print("\nTemplate would access:")
print(f"  Link text: {enhanced['_link_text']}")
print(f"  Link URL: {enhanced['_link_url']}")
print(f"  Age range: {enhanced['age_range']}")
print(f"  Material: {enhanced['material']}")