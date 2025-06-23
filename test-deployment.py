#!/usr/bin/env python3
"""
Integration test for Azure Container App deployment.
Tests critical functionality of the deployed application.
"""

import requests
import sys
import time
from urllib.parse import urljoin

# Production URLs
BASE_URLS = [
    "https://nobsmed.com",
    "https://www.nobsmed.com",
    "https://nobswebsite.whitemushroom-20288100.westus.azurecontainerapps.io"
]

def test_health_check(base_url: str) -> bool:
    """Test basic health/homepage endpoint."""
    try:
        response = requests.get(base_url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed for {base_url}: {e}")
        return False

def test_search_endpoint(base_url: str) -> bool:
    """Test search functionality with a sample query."""
    try:
        search_url = urljoin(base_url, "/search")
        params = {"question": "vitamin d deficiency"}
        response = requests.get(search_url, params=params, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ Search endpoint returned {response.status_code}")
            return False
            
        # Check for key elements in response
        content = response.text.lower()
        required_elements = [
            "search results for",
            "vitamin d deficiency",
            "resulting experience"
        ]
        
        for element in required_elements:
            if element not in content:
                print(f"❌ Missing required element: {element}")
                return False
                
        return True
    except Exception as e:
        print(f"❌ Search test failed for {base_url}: {e}")
        return False

def test_static_resources(base_url: str) -> bool:
    """Test that static resources are loading."""
    try:
        favicon_url = urljoin(base_url, "/static/favicon.ico")
        response = requests.get(favicon_url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Static resource test failed for {base_url}: {e}")
        return False

def run_integration_tests():
    """Run all integration tests against production deployment."""
    print("🚀 Starting Azure Container App Integration Tests")
    print("=" * 60)
    
    all_passed = True
    
    for base_url in BASE_URLS:
        print(f"\n🔍 Testing: {base_url}")
        
        # Test 1: Health Check
        print("  ├─ Health check...", end=" ")
        if test_health_check(base_url):
            print("✅ PASS")
        else:
            print("❌ FAIL")
            all_passed = False
            
        # Test 2: Search Functionality
        print("  ├─ Search endpoint...", end=" ")
        if test_search_endpoint(base_url):
            print("✅ PASS")
        else:
            print("❌ FAIL")
            all_passed = False
            
        # Test 3: Static Resources
        print("  └─ Static resources...", end=" ")
        if test_static_resources(base_url):
            print("✅ PASS")
        else:
            print("❌ FAIL")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Deployment successful!")
        return 0
    else:
        print("💥 SOME TESTS FAILED - Check deployment!")
        return 1

if __name__ == "__main__":
    # Wait a moment for deployment to stabilize
    print("⏳ Waiting 10 seconds for deployment to stabilize...")
    time.sleep(10)
    
    exit_code = run_integration_tests()
    sys.exit(exit_code)