#!/usr/bin/env python3
"""
Check if the short amzn.to URLs resolve to the same products as the full Amazon URLs
by making a HEAD request to get the final redirect URL.
"""

import requests
import re
from website.jennas_amazon_products import (
    infant_bath_tubs,
    infant_laundry_detergents,
    infant_care_books,
    infant_high_chairs,
)

def extract_asin(url):
    """Extract ASIN from Amazon URL"""
    if not url:
        return None
    
    # Pattern for ASIN in Amazon URLs
    asin_patterns = [
        r'/dp/([A-Z0-9]{10})',
        r'/gp/product/([A-Z0-9]{10})',
        r'ASIN=([A-Z0-9]{10})',
        r'/([A-Z0-9]{10})/',
    ]
    
    for pattern in asin_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def resolve_short_url(short_url):
    """Resolve a short URL to its final destination"""
    try:
        response = requests.head(short_url, allow_redirects=True, timeout=10)
        return response.url
    except Exception as e:
        print(f"Error resolving {short_url}: {e}")
        return None

def check_short_url_matches():
    """Check if short URLs resolve to the same ASINs as full URLs"""
    test_cases = [
        ("Skip Hop Moby Smart Sling 3‑Stage", "https://amzn.to/4npcr7B", "https://www.amazon.com/Skip-Hop-Moby-Smart-Sling/dp/B07FK7BG98/ref=nosim?tag=nobsmed07-20"),
        ("Angelcare Soft‑Touch Bath Support", "https://amzn.to/3FVGZgm", "https://www.amazon.com/Angelcare-Baby-Bath-Support-Grey/dp/B01M6YVW7B/ref=nosim?tag=nobsmed07-20"),
        ("Baby Delight Cushy Nest Cloud", "https://amzn.to/4lkvBcL", "https://www.amazon.com/Baby-Delight-Premium-Organic-Comfortable/dp/B0CSMDJ636/ref=nosim?tag=nobsmed07-20"),
        ("Puj Flyte Compact Infant Bath", "https://amzn.to/45FNNJu", "https://www.amazon.com/Puj-Flyte-Compact-Infant-Bathtub/dp/B008PZ9VXY/ref=nosim?tag=nobsmed07-20"),
        ("Dreft Stage 1", "https://amzn.to/40kdY4E", "https://www.amazon.com/Dreft-Stage-Newborn-Liquid-Detergent/dp/B004HXI3Y0/ref=nosim?tag=nobsmed07-20"),
        ("Babyganics 3X", "https://amzn.to/44lhkWw", "https://www.amazon.com/Babyganics-Laundry-Detergent-Concentrated-Fragrance/dp/B07BHVK34S/ref=nosim?tag=nobsmed07-20"),
        ("What to Expect", "https://amzn.to/45Dn4gD", "https://www.amazon.com/What-Expect-First-Heidi-Murkoff/dp/0761187480/ref=nosim?tag=nobsmed07-20"),
        ("Joovy Nook", "https://amzn.to/4npgRvd", "https://www.amazon.com/Joovy-Nook-High-Chair/dp/B00FQ0G8I0/ref=nosim?tag=nobsmed07-20"),
    ]
    
    print("Checking if short URLs resolve to same ASINs as full URLs...")
    print("=" * 80)
    
    for name, short_url, full_url in test_cases:
        print(f"\nProduct: {name}")
        print(f"Short URL: {short_url}")
        print(f"Full URL:  {full_url}")
        
        # Resolve the short URL
        resolved_url = resolve_short_url(short_url)
        if resolved_url:
            print(f"Resolved:  {resolved_url}")
            
            # Extract ASINs
            short_asin = extract_asin(resolved_url)
            full_asin = extract_asin(full_url)
            
            print(f"Short ASIN: {short_asin}")
            print(f"Full ASIN:  {full_asin}")
            
            if short_asin == full_asin:
                print("✅ MATCH - Same product")
            else:
                print("❌ DIFFERENT - Different products")
        else:
            print("❌ Could not resolve short URL")
        
        print("-" * 40)

if __name__ == "__main__":
    check_short_url_matches()