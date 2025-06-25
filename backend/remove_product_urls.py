#!/usr/bin/env python3
"""
Remove product_url fields and consolidate to amazon_url only
"""
import re

def process_file():
    with open('website/jennas_amazon_products.py', 'r') as f:
        content = f.read()
    
    # Remove product_url lines from dictionaries
    # This pattern matches lines like: "product_url": "https://...",
    pattern = r'\s*"product_url":\s*"[^"]+",?\s*\n'
    content = re.sub(pattern, '', content)
    
    # Also remove any amzn.to comments that reference old short URLs
    pattern = r'\s*#\s*https://amzn\.to/[^\n]*\n'
    content = re.sub(pattern, '', content)
    
    with open('website/jennas_amazon_products.py', 'w') as f:
        f.write(content)
    
    print("✅ Removed all product_url fields from dictionaries")
    print("✅ Kept amazon_url fields with referral tags")
    print("✅ InfantProduct.product_url property provides backwards compatibility")

if __name__ == "__main__":
    process_file()