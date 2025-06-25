#!/usr/bin/env python3
"""
Test the fixed links
"""
import requests
import time

# The fixed URLs
fixed_urls = [
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
        
        if "Page Not Found" in response.text or "Sorry, we couldn't find that page" in response.text:
            print(f"❌ {name}: BROKEN - Page Not Found")
            return False
        elif "/s?" in response.url:  # Redirected to search
            print(f"❌ {name}: BROKEN - Redirects to search")
            return False
        elif response.status_code == 200:
            print(f"✅ {name}: WORKING")
            return True
        else:
            print(f"❌ {name}: BROKEN - Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        return False

print("Testing fixed Amazon product links...")
print("=" * 60)

all_working = True
for url, name in zip(fixed_urls, product_names):
    if not test_url(url, name):
        all_working = False
    time.sleep(1)

print("=" * 60)
if all_working:
    print("🎉 All links are now working!")
else:
    print("⚠️  Some links still have issues")