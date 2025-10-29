#!/usr/bin/env python3
"""
Extract all 80 products from shopping_tools.py to JSON format
"""

import json
from shopping_tools import get_all_products

# Get all products
products = get_all_products()

# Create product catalog with all data
catalog = {
    "total_products": len(products),
    "categories": {},
    "products": products
}

# Organize by category
for product in products:
    category = product.get('category', 'other')
    if category not in catalog['categories']:
        catalog['categories'][category] = []
    catalog['categories'][category].append(product)

# Save to JSON file
with open('products-catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Extracted {len(products)} products")
print(f"Categories: {', '.join(catalog['categories'].keys())}")
print(f"Saved to: products-catalog.json")

# Create simplified version for website (just the products array)
with open('products-simple.json', 'w', encoding='utf-8') as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print(f"Saved simple version to: products-simple.json")

