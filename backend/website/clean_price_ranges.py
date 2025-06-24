#!/usr/bin/env python3
"""Script to clean up price_range fields in jennas_amazon_products.py"""

import re
from pathlib import Path

def clean_price_ranges():
    file_path = Path(__file__).parent / "jennas_amazon_products.py"
    
    # Read the file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Define patterns to clean up price_range fields
    patterns = [
        # Mid-range (~$40) -> $40
        (r'"price_range": "Mid-range \(~\$([^)]+)\)"', r'"price_range": "$\1"'),
        # Budget-friendly (~$25–35) -> $25–35
        (r'"price_range": "Budget-friendly \(~\$([^)]+)\)"', r'"price_range": "$\1"'),
        # Budget (~$35) -> $35
        (r'"price_range": "Budget \(~\$([^)]+)\)"', r'"price_range": "$\1"'),
        # Mid to high (~$15–18 for 50 oz) -> $15–18
        (r'"price_range": "Mid to high \(~\$([^)]+)\)"', r'"price_range": "$\1"'),
        # Premium (~$200–300) -> $200–300
        (r'"price_range": "Premium \(~\$([^)]+)\)"', r'"price_range": "$\1"'),
        # Budget to mid (~$30–50) -> $30–50
        (r'"price_range": "Budget to mid \(~\$([^)]+)\)"', r'"price_range": "$\1"'),
        # High-end (~$250–350) -> $250–350
        (r'"price_range": "High-end \(~\$([^)]+)\)"', r'"price_range": "$\1"'),
        # Luxury (~$400–600) -> $400–600
        (r'"price_range": "Luxury \(~\$([^)]+)\)"', r'"price_range": "$\1"'),
        # Remove " for X oz" or " for set" from price ranges
        (r'"price_range": "\$([^"]+) for [^"]*"', r'"price_range": "$\1"'),
        # Any remaining pattern with descriptive text
        (r'"price_range": "[^"]*\(~\$([^)]+)\)"', r'"price_range": "$\1"'),
    ]
    
    # Apply each pattern
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # Write back to file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("Price range cleanup completed!")

if __name__ == "__main__":
    clean_price_ranges()