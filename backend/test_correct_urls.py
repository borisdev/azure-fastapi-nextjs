#!/usr/bin/env python3
"""
Test the correct Amazon URLs to verify they show actual product pages
"""
import requests
import time

# URLs to test
test_urls = [
    ("Graco Blossom 6-in-1", "https://www.amazon.com/dp/B08C6ZD793/ref=nosim?tag=nobsmed07-20"),
    ("Inglesina Fast Table Chair", "https://www.amazon.com/dp/B00IOGIM9S/ref=nosim?tag=nobsmed07-20"),
    ("Fisher-Price SpaceSaver", "https://www.amazon.com/dp/B08KFQK84Q/ref=nosim?tag=nobsmed07-20")
]

def test_url(name: str, url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        
        # Check for various error conditions
        if response.status_code != 200:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
            
        content = response.text.lower()
        
        # Check if redirected to search page
        if "/s?" in response.url or "search" in response.url:
            print(f"❌ {name}: Redirected to search page")
            return False
            
        # Check for error pages
        error_phrases = [
            "page not found",
            "sorry, we couldn't find that page",
            "looking for something?",
            "we can't find that page",
            "does not exist",
            "no longer available"
        ]
        
        for phrase in error_phrases:
            if phrase in content:
                print(f"❌ {name}: Error page detected - {phrase}")
                return False
        
        # Check for positive indicators of a product page
        product_indicators = [
            "add to cart",
            "buy now",
            "price",
            "shipping",
            "customer reviews",
            "product details"
        ]
        
        found_indicators = sum(1 for indicator in product_indicators if indicator in content)
        
        if found_indicators >= 3:
            print(f"✅ {name}: Valid product page (found {found_indicators} indicators)")
            return True
        else:
            print(f"⚠️  {name}: Questionable page (only {found_indicators} indicators)")
            return False
            
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False

print("Testing correct Amazon URLs...")
print("=" * 60)

all_working = True
for name, url in test_urls:
    print(f"\nTesting: {name}")
    print(f"URL: {url}")
    if not test_url(name, url):
        all_working = False
    time.sleep(2)  # Be nice to Amazon

print("\n" + "=" * 60)
if all_working:
    print("🎉 All URLs are valid product pages!")
else:
    print("⚠️  Some URLs may have issues")