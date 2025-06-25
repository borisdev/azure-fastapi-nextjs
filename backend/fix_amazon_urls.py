#!/usr/bin/env python3
"""
Update Amazon product URLs with working links and referral tags
"""

# Correct Amazon ASINs found from Google search
correct_products = {
    "Graco Blossom 6-in-1 Convertible High Chair": {
        "asin": "B08C6ZD793",  # Redmond color variant - most popular
        "title": "Graco Blossom 6 in 1 Convertible High Chair, Redmond"
    },
    "Inglesina Fast Table Chair": {
        "asin": "B00IOGIM9S",  # Black color - original/most popular
        "title": "Inglesina Fast Table Chair, Black"
    },
    "Fisher-Price SpaceSaver High Chair": {
        "asin": "B08KFQK84Q",  # Latest Simple Clean model
        "title": "Fisher-Price Baby to Toddler High Chair SpaceSaver Simple Clean"
    }
}

# Generate URLs with affiliate tag
affiliate_tag = "nobsmed07-20"

print("Correct Amazon URLs with affiliate tags:")
print("=" * 60)

for product_name, info in correct_products.items():
    url = f"https://www.amazon.com/dp/{info['asin']}/ref=nosim?tag={affiliate_tag}"
    print(f"\n{product_name}:")
    print(f"  ASIN: {info['asin']}")
    print(f"  Title: {info['title']}")
    print(f"  URL: {url}")

print("\n" + "=" * 60)
print("These URLs should be used to replace the broken links in jennas_amazon_products.py")