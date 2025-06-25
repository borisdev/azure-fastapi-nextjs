#!/usr/bin/env python3
"""
Test Amazon product links to find broken ones
"""
import requests
import time
from typing import List, Tuple
import sys

# Amazon shortened URLs from the product data
amazon_short_urls = [
    "https://amzn.to/3FVGZgm",
    "https://amzn.to/3ZKr2QS", 
    "https://amzn.to/409hMGb",
    "https://amzn.to/40kdY4E",
    "https://amzn.to/43YvmON",
    "https://amzn.to/44hNBh5",
    "https://amzn.to/44lhkWw",
    "https://amzn.to/45Dn4gD",
    "https://amzn.to/45FNNJu",
    "https://amzn.to/45zctTO",
    "https://amzn.to/469uIzk",
    "https://amzn.to/46birdL",
    "https://amzn.to/4ehqesv",
    "https://amzn.to/4ei9KQZ",
    "https://amzn.to/4k7vlNq",
    "https://amzn.to/4lkvBcL",
    "https://amzn.to/4npcr7B",
    "https://amzn.to/4npgRvd"
]

def test_url(url: str) -> Tuple[str, int, str]:
    """Test a single URL and return status info"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        final_url = response.url
        
        # Check if we ended up on an Amazon error page
        if "Page Not Found" in response.text or "Sorry, we couldn't find that page" in response.text:
            return url, response.status_code, "ERROR: Page Not Found"
        elif "amazon.com" not in final_url:
            return url, response.status_code, f"ERROR: Redirected outside Amazon to {final_url}"
        else:
            return url, response.status_code, f"OK: Redirects to {final_url}"
            
    except requests.RequestException as e:
        return url, 0, f"ERROR: {str(e)}"

def main():
    print("Testing Amazon product links...")
    print("=" * 60)
    
    broken_links = []
    working_links = []
    
    for i, url in enumerate(amazon_short_urls, 1):
        print(f"Testing {i}/{len(amazon_short_urls)}: {url}")
        
        original_url, status_code, message = test_url(url)
        
        if status_code != 200 or "ERROR" in message:
            broken_links.append((original_url, status_code, message))
            print(f"  ❌ BROKEN: {message}")
        else:
            working_links.append((original_url, status_code, message))
            print(f"  ✅ OK: Status {status_code}")
        
        # Rate limiting - be nice to Amazon
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Working links: {len(working_links)}")
    print(f"Broken links: {len(broken_links)}")
    
    if broken_links:
        print("\nBROKEN LINKS:")
        for url, status, message in broken_links:
            print(f"  {url} - {message}")
    
    return len(broken_links)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)