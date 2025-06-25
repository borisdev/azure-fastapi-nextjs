#!/usr/bin/env python3
"""
Analyze jennas_amazon_products.py to find products with both product_url and amazon_url
and compare their URLs for consolidation.
"""

import re
from urllib.parse import urlparse, parse_qs
from website.jennas_amazon_products import (
    infant_bath_tubs,
    infant_laundry_detergents,
    infant_care_books,
    bottle_cleaners,
    bottle_sanitizers,
    bottle_dryers,
    infant_high_chairs,
    infant_nursing_pillows,
    non_toxic_playmats,
    baby_carrier_wraps,
    post_delivery_healing_products,
    non_toxic_infant_car_seats,
    non_toxic_bassinets,
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

def has_referral_tag(url, tag="nobsmed07-20"):
    """Check if URL contains the referral tag"""
    if not url:
        return False
    return tag in url

def analyze_url_differences(product_url, amazon_url):
    """Analyze differences between two URLs"""
    if not product_url or not amazon_url:
        return "One URL is missing"
    
    # Check if they're fundamentally different products
    asin1 = extract_asin(product_url)
    asin2 = extract_asin(amazon_url)
    
    if asin1 and asin2 and asin1 != asin2:
        return f"Different ASINs: {asin1} vs {asin2}"
    
    # Check if one is a short URL and one is full
    if "amzn.to" in product_url and "amazon.com" in amazon_url:
        return "Short URL vs Full URL"
    
    # Check referral tags
    has_ref1 = has_referral_tag(product_url)
    has_ref2 = has_referral_tag(amazon_url)
    
    if has_ref1 != has_ref2:
        return f"Referral tag difference: product_url={has_ref1}, amazon_url={has_ref2}"
    
    return "Similar URLs"

def analyze_products():
    """Analyze all product collections"""
    all_collections = [
        ("infant_bath_tubs", infant_bath_tubs),
        ("infant_laundry_detergents", infant_laundry_detergents),
        ("infant_care_books", infant_care_books),
        ("bottle_cleaners", bottle_cleaners),
        ("bottle_sanitizers", bottle_sanitizers),
        ("bottle_dryers", bottle_dryers),
        ("infant_high_chairs", infant_high_chairs),
        ("infant_nursing_pillows", infant_nursing_pillows),
        ("non_toxic_playmats", non_toxic_playmats),
        ("baby_carrier_wraps", baby_carrier_wraps),
        ("post_delivery_healing_products", post_delivery_healing_products),
        ("non_toxic_infant_car_seats", non_toxic_infant_car_seats),
        ("non_toxic_bassinets", non_toxic_bassinets),
    ]
    
    results = []
    
    for collection_name, collection in all_collections:
        for i, product in enumerate(collection):
            product_url = product.get("product_url")
            amazon_url = product.get("amazon_url")
            name = product.get("name", f"Product {i+1}")
            
            if product_url and amazon_url:
                analysis = {
                    "collection": collection_name,
                    "name": name,
                    "product_url": product_url,
                    "amazon_url": amazon_url,
                    "product_url_asin": extract_asin(product_url),
                    "amazon_url_asin": extract_asin(amazon_url),
                    "product_url_has_referral": has_referral_tag(product_url),
                    "amazon_url_has_referral": has_referral_tag(amazon_url),
                    "difference_analysis": analyze_url_differences(product_url, amazon_url),
                }
                results.append(analysis)
    
    return results

def print_analysis(results):
    """Print detailed analysis results"""
    print("=" * 80)
    print("PRODUCT URL ANALYSIS REPORT")
    print("=" * 80)
    print()
    
    # Summary statistics
    total_products = len(results)
    different_asins = sum(1 for r in results if r["product_url_asin"] != r["amazon_url_asin"])
    both_have_referral = sum(1 for r in results if r["product_url_has_referral"] and r["amazon_url_has_referral"])
    only_product_url_has_referral = sum(1 for r in results if r["product_url_has_referral"] and not r["amazon_url_has_referral"])
    only_amazon_url_has_referral = sum(1 for r in results if not r["product_url_has_referral"] and r["amazon_url_has_referral"])
    
    print(f"SUMMARY:")
    print(f"Total products with both URLs: {total_products}")
    print(f"Products with different ASINs: {different_asins}")
    print(f"Products where both URLs have referral tag: {both_have_referral}")
    print(f"Products where only product_url has referral tag: {only_product_url_has_referral}")
    print(f"Products where only amazon_url has referral tag: {only_amazon_url_has_referral}")
    print()
    
    # Detailed analysis
    print("DETAILED ANALYSIS:")
    print("-" * 80)
    
    for result in results:
        print(f"\nCollection: {result['collection']}")
        print(f"Product: {result['name']}")
        print(f"Product URL: {result['product_url']}")
        print(f"Amazon URL:  {result['amazon_url']}")
        print(f"Product URL ASIN: {result['product_url_asin']}")
        print(f"Amazon URL ASIN:  {result['amazon_url_asin']}")
        print(f"Product URL has referral: {result['product_url_has_referral']}")
        print(f"Amazon URL has referral:  {result['amazon_url_has_referral']}")
        print(f"Analysis: {result['difference_analysis']}")
        print("-" * 40)

def recommend_consolidation(results):
    """Recommend which URL to keep for each product"""
    print("\n" + "=" * 80)
    print("CONSOLIDATION RECOMMENDATIONS")
    print("=" * 80)
    
    for result in results:
        print(f"\nProduct: {result['name']} ({result['collection']})")
        
        # Decision logic
        if result['product_url_asin'] != result['amazon_url_asin']:
            print("❌ DIFFERENT PRODUCTS - MANUAL REVIEW REQUIRED")
            print(f"   Product URL ASIN: {result['product_url_asin']}")
            print(f"   Amazon URL ASIN:  {result['amazon_url_asin']}")
            continue
        
        # Both URLs point to same product, decide which to keep
        recommended_url = None
        reason = ""
        
        if result['amazon_url_has_referral'] and not result['product_url_has_referral']:
            recommended_url = result['amazon_url']
            reason = "Amazon URL has referral tag, product URL doesn't"
        elif result['product_url_has_referral'] and not result['amazon_url_has_referral']:
            recommended_url = result['product_url']
            reason = "Product URL has referral tag, amazon URL doesn't"
        elif result['amazon_url_has_referral'] and result['product_url_has_referral']:
            # Both have referral tags, prefer the full Amazon URL over short URLs
            if "amzn.to" in result['product_url'] and "amazon.com" in result['amazon_url']:
                recommended_url = result['amazon_url']
                reason = "Both have referral tags, prefer full Amazon URL over short URL"
            else:
                recommended_url = result['amazon_url']
                reason = "Both have referral tags, keeping amazon_url for consistency"
        else:
            # Neither has referral tag, add it to the full URL
            if "amazon.com" in result['amazon_url']:
                # Add referral tag to amazon_url
                if "?" in result['amazon_url']:
                    recommended_url = result['amazon_url'] + "&tag=nobsmed07-20"
                else:
                    recommended_url = result['amazon_url'] + "?tag=nobsmed07-20"
                reason = "Neither had referral tag, added to full Amazon URL"
            else:
                recommended_url = result['product_url']
                reason = "Neither had referral tag, keeping product_url"
        
        print(f"✅ RECOMMEND: {recommended_url}")
        print(f"   Reason: {reason}")

if __name__ == "__main__":
    results = analyze_products()
    print_analysis(results)
    recommend_consolidation(results)