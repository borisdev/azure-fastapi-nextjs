#!/usr/bin/env python3
"""
Fix formatting issues where { got merged with first field
"""
import re

def fix_formatting():
    with open('website/jennas_amazon_products.py', 'r') as f:
        content = f.read()
    
    # Fix lines like: "{        "name": " → {
    #                                        "name": "
    pattern = r'\{\s*"([a-zA-Z_]+)": "'
    content = re.sub(pattern, r'{\n        "\1": "', content)
    
    # Fix other field patterns that may have gotten merged
    pattern = r'\{\s*#'
    content = re.sub(pattern, r'{\n        #', content)
    
    with open('website/jennas_amazon_products.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed formatting issues")

if __name__ == "__main__":
    fix_formatting()