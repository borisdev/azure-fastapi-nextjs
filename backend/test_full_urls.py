#!/usr/bin/env python3
"""
Test the full Amazon URLs for the broken products
"""
import requests
import time

# Full Amazon URLs for the broken products
full_urls = [
    "https://www.amazon.com/Graco-Blossom-Convertible-High-Chair/dp/B00I8JZ1H4/ref=nosim?tag=nobsmed07-20",
    "https://www.amazon.com/Inglesina-Fast-Table-Chair/dp/B00O7SS3AA/ref=nosim?tag=nobsmed07-20", 
    "https://www.amazon.com/Fisher-Price-SpaceSaver-High-Chair/dp/B01M8H9QVU/ref=nosim?tag=nobsmed07-20"
]

product_names = [
    "Graco Blossom 6-in-1 Convertible High Chair",
    "Inglesina Fast Table Chair",
    "Fisher-Price SpaceSaver High Chair"
]

def test_url(url: str, name: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"\n{name}:")
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        print(f"  Final URL: {response.url}")
        
        if "Page Not Found" in response.text or "Sorry, we couldn't find that page" in response.text:
            print(f"  Result: ❌ BROKEN - Page Not Found")
            return False
        elif "/s?" in response.url:  # Redirected to search
            print(f"  Result: ❌ BROKEN - Redirects to search")
            return False
        elif response.status_code == 200:
            print(f"  Result: ✅ WORKING")
            return True
        else:
            print(f"  Result: ❌ BROKEN - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  Result: ❌ ERROR - {e}")
        return False

print("Testing full Amazon URLs for broken products...")
print("=" * 60)

for url, name in zip(full_urls, product_names):
    test_url(url, name)
    time.sleep(1)