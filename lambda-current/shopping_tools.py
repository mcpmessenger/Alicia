# shopping_tools.py
# Updated to load from products-simple.json

import os
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AMAZON_PARTNER_TAG = os.environ.get('AMAZON_PARTNER_TAG', 'aipro00-20')

def get_all_products() -> List[Dict[str, Any]]:
    """
    Load all 108 products from products-simple.json
    """
    try:
        # Try to load from file in Lambda package
        json_path = os.path.join(os.path.dirname(__file__), 'products-simple.json')
        
        if not os.path.exists(json_path):
            logger.error(f"products-simple.json not found at {json_path}")
            # Return empty list if file not found
            return []
        
        with open(json_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        logger.info(f"Successfully loaded {len(products)} products from JSON")
        return products
        
    except Exception as e:
        logger.error(f"Error loading products: {str(e)}")
        return []

def search_products(query: str, max_price: Optional[float] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search through all products"""
    all_products = get_all_products()
    
    # Filter by category if specified
    if category:
        all_products = [p for p in all_products if p.get('category') == category or p.get('subcategory') == category]
    
    # Convert query to lowercase for case-insensitive search
    query_lower = query.lower()
    query_words = query_lower.split()
    
    scored_products = []
    for product in all_products:
        score = 0
        name_lower = product.get('name', '').lower()
        desc_lower = product.get('description', '').lower()
        cat_lower = product.get('category', '').lower()
        subcat_lower = product.get('subcategory', '').lower()
        
        # Score based on matches
        for word in query_words:
            if word in name_lower:
                score += 10
            if word in desc_lower:
                score += 5
            if word in cat_lower:
                score += 3
            if word in subcat_lower:
                score += 3
        
        # Only include products with decent score (at least one match)
        if score > 0:
            product['_search_score'] = score
            scored_products.append(product)
    
    # If NO matches at all, return empty list (no random products!)
    if not scored_products:
        return []
    
    # Filter by price if specified
    if max_price:
        scored_products = [p for p in scored_products if p['price'] <= max_price]
    
    # Sort by search score and rating
    scored_products.sort(key=lambda x: (x.get('_search_score', 0), x.get('rating', 0)), reverse=True)
    
    return scored_products[:15]  # Return top 15 matches

def product_search_tool(query: str, category: Optional[str] = None, max_price: Optional[float] = None) -> Dict[str, Any]:
    """
    Main product search function that Alexa uses
    """
    try:
        products = search_products(query, max_price=max_price, category=category)
        
        if not products:
            return {
                'success': False,
                'message': f"I couldn't find any products matching '{query}'",
                'products': []
            }
        
        return {
            'success': True,
            'message': f"I found {len(products)} products matching '{query}'",
            'products': products
        }
    
    except Exception as e:
        logger.error(f"Error in product_search_tool: {str(e)}")
        return {
            'success': False,
            'message': f"Sorry, there was an error searching for products: {str(e)}",
            'products': []
        }

def affiliate_injector(asin: str) -> str:
    """Generate Amazon affiliate URL with partner tag"""
    return f"https://www.amazon.com/dp/{asin}?tag={AMAZON_PARTNER_TAG}"

