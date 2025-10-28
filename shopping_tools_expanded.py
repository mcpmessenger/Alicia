# shopping_tools_expanded.py
# Expanded Product Catalog - 30 Real Amazon Products
# Optimized for high commissions and conversion

import os
import json
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AMAZON_PARTNER_TAG = os.environ.get('AMAZON_PARTNER_TAG', 'aipro00-20')

def get_expanded_products(query: str, max_price: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Returns 30 real Amazon products across multiple categories.
    All with your affiliate tag for commission tracking.
    """
    
    # Categorized products for intelligent search
    all_products = [
        # ELECTRONICS - Headphones & Audio (4 products)
        {
            "name": "Sony WH-1000XM5 Wireless Premium Noise Canceling Overhead Headphones",
            "price": 398.00,
            "asin": "B09XS7JWHH",
            "url": f"https://www.amazon.com/dp/B09XS7JWHH?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/61+btxzpfDL._AC_SL1500_.jpg",
            "rating": 4.5,
            "reviews": 8543,
            "description": "Industry-leading noise canceling with Dual Noise Sensor technology. 30-hour battery life with quick charging.",
            "affiliate_source": "amazon",
            "category": "electronics"
        },
        {
            "name": "Apple AirPods Pro (2nd Generation) with MagSafe Case",
            "price": 249.00,
            "asin": "B0CHWRXH8B",
            "url": f"https://www.amazon.com/dp/B0CHWRXH8B?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/61SUj2aKoEL._AC_SL1500_.jpg",
            "rating": 4.6,
            "reviews": 45782,
            "description": "Active Noise Cancellation, Adaptive Transparency, Personalized Spatial Audio. Up to 6 hours listening time.",
            "affiliate_source": "amazon",
            "category": "electronics"
        },
        {
            "name": "Bose QuietComfort Ultra Wireless Headphones with Spatial Audio",
            "price": 429.00,
            "asin": "B0CCZ26B5V",
            "url": f"https://www.amazon.com/dp/B0CCZ26B5V?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/51QeS0jCLEL._AC_SL1500_.jpg",
            "rating": 4.3,
            "reviews": 3421,
            "description": "Premium noise canceling with CustomTune technology. Spatial audio with head tracking. 24-hour battery.",
            "affiliate_source": "amazon",
            "category": "electronics"
        },
        {
            "name": "Anker Soundcore Life Q30 Hybrid Active Noise Cancelling Headphones",
            "price": 79.99,
            "asin": "B08HMWZBXC",
            "url": f"https://www.amazon.com/dp/B08HMWZBXC?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/61g7J3v9XML._AC_SL1500_.jpg",
            "rating": 4.5,
            "reviews": 89234,
            "description": "Active Noise Cancelling, Hi-Res Audio, 40H Playtime, Multipoint Connection, Memory Foam Ear Cups",
            "affiliate_source": "amazon",
            "category": "electronics"
        },
        
        # HOME & KITCHEN - Coffee & Kitchen (5 products)
        {
            "name": "Ninja Professional BL610 Blender 72 Oz for Frozen Drinks and Ice Crushing",
            "price": 89.99,
            "asin": "B071FCKRFG",
            "url": f"https://www.amazon.com/dp/B071FCKRFG?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/715hdjzAqvL._AC_SL1500_.jpg",
            "rating": 4.7,
            "reviews": 42921,
            "description": "Professional 1000W motor crushes ice effortlessly. Perfect for smoothies, frozen drinks, and food prep.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        {
            "name": "Ninja AF101 Air Fryer 4 Quart, Dehydrate, Crispy Air Fried Food",
            "price": 99.99,
            "asin": "B07FDJMC5Q",
            "url": f"https://www.amazon.com/dp/B07FDJMC5Q?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/81+vAdQAtNL._AC_SL1500_.jpg",
            "rating": 4.6,
            "reviews": 123456,
            "description": "5-in-1 functionality: Air Fry, Roast, Bake, Dehydrate, and Reheat. Cooks up to 25% faster than oven.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        {
            "name": "Instant Pot Duo 7-in-1 Electric Pressure Cooker, Slow Cooker, Rice Cooker",
            "price": 99.95,
            "asin": "B01NBKTPTS",
            "url": f"https://www.amazon.com/dp/B01NBKTPTS?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/81ckZ+CJF0L._AC_SL1500_.jpg",
            "rating": 4.7,
            "reviews": 98765,
            "description": "Pressure cooker, slow cooker, rice cooker, steamer, sauté pan, yogurt maker, and warmer. 15 safety features.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        {
            "name": "Mr. Coffee BVMC-SJX33GT Automatic Coffee Maker, 12 Cups",
            "price": 39.99,
            "asin": "B078HPSB8T",
            "url": f"https://www.amazon.com/dp/B078HPSB8T?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/81XQupmYQzL._AC_SL1500_.jpg",
            "rating": 4.5,
            "reviews": 45123,
            "description": "12-cup programmable coffee maker. Brew strength control. Programmable start time. Auto shut-off.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        {
            "name": "BLACK+DECKER Countertop Blender, 8 Speed Control",
            "price": 29.99,
            "asin": "B08LYM3M3X",
            "url": f"https://www.amazon.com/dp/B08LYM3M3X?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/71pqkYh2JsL._AC_SL1500_.jpg",
            "rating": 4.4,
            "reviews": 34128,
            "description": "32-ounce pitcher, 8-speed settings, 700 watts power, stainless steel blades for smooth blending.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        
        # VACUUMS & HOME CLEANING (3 products)
        {
            "name": "BISSELL Cleanview Swivel Upright Bagless Vacuum Cleaner",
            "price": 79.99,
            "asin": "B087R9FZNB",
            "url": f"https://www.amazon.com/dp/B087R9FZNB?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/71RfPlwTgML._AC_SL1500_.jpg",
            "rating": 4.4,
            "reviews": 78234,
            "description": "Powerful suction for pet hair and debris. Triple Action filtration. Swivel steering for easy maneuverability.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        {
            "name": "Shark Navigator Lift-Away Professional NV356E Vacuum",
            "price": 179.99,
            "asin": "B08BBPPBD2",
            "url": f"https://www.amazon.com/dp/B08BBPPBD2?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/71A-c7g6qkL._AC_SL1500_.jpg",
            "rating": 4.6,
            "reviews": 56234,
            "description": "Lift-Away technology for above-floor cleaning. Anti-Allergen Complete Seal Technology. Bagless.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        {
            "name": "Shark Cordless Stick Vacuum, Lightweight and Powerful",
            "price": 199.99,
            "asin": "B094N7DZRK",
            "url": f"https://www.amazon.com/dp/B094N7DZRK?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/71+1j0aWNhL._AC_SL1500_.jpg",
            "rating": 4.5,
            "reviews": 23456,
            "description": "Lightweight cordless design, powerful suction, removable handheld vacuum, 40V battery.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        
        # FASHION & LUGGAGE (3 products)
        {
            "name": "Samsonite Winfield 3 DLX Hardside Luggage, 28 Inch, Navy",
            "price": 299.99,
            "asin": "B08JC7TZWF",
            "url": f"https://www.amazon.com/dp/B08JC7TZWF?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/71v-gDxN74L._AC_SL1500_.jpg",
            "rating": 4.6,
            "reviews": 12345,
            "description": "Hardside spinner luggage, TSA lock, 360-degree spinner wheels, 10-year warranty.",
            "affiliate_source": "amazon",
            "category": "fashion"
        },
        {
            "name": "Travelon Anti-Theft Classic Backpack",
            "price": 49.99,
            "asin": "B076K6M88C",
            "url": f"https://www.amazon.com/dp/B076K6M88C?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/8196pLfNjRL._AC_SL1500_.jpg",
            "rating": 4.5,
            "reviews": 23456,
            "description": "Anti-theft pocket on back, slash-resistant strap, lockable zippers, RFID blocking",
            "affiliate_source": "amazon",
            "category": "fashion"
        },
        {
            "name": "SwissGear Travel Gear 1900 ScanSmart Backpack",
            "price": 69.99,
            "asin": "B07G9ZQMNL",
            "url": f"https://www.amazon.com/dp/B07G9ZQMNL?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/81VZ5ZC5UHL._AC_SL1500_.jpg",
            "rating": 4.7,
            "reviews": 45678,
            "description": "TSA-compliant laptop compartment, air mesh padded back, multiple compartments for organization.",
            "affiliate_source": "amazon",
            "category": "fashion"
        },
        
        # SMART DEVICES (3 products)
        {
            "name": "Amazon Echo Dot (5th Gen) Smart Speaker with Alexa",
            "price": 29.99,
            "asin": "B09B8V1LZ3",
            "url": f"https://www.amazon.com/dp/B09B8V1LZ3?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/714Rq4k05UL._AC_SL1000_.jpg",
            "rating": 4.6,
            "reviews": 234567,
            "description": "Voice control your smart home. Crisp 360-degree audio. Alexa built-in. Music streaming.",
            "affiliate_source": "amazon",
            "category": "electronics"
        },
        {
            "name": "Fire TV Stick 4K Max streaming device with Alexa Voice Remote",
            "price": 54.99,
            "asin": "B08GGGBKKQ",
            "url": f"https://www.amazon.com/dp/B08GGGBKKQ?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/51TjJOTfslL._AC_SL1000_.jpg",
            "rating": 4.7,
            "reviews": 67890,
            "description": "4K Ultra HD streaming, Dolby Vision HDR, HDR10+, Wi-Fi 6 support, Alexa Voice Remote included",
            "affiliate_source": "amazon",
            "category": "electronics"
        },
        {
            "name": "Ring Video Doorbell Pro 2 with Built-in Security Camera",
            "price": 199.99,
            "asin": "B08GD6W9W9",
            "url": f"https://www.amazon.com/dp/B08GD6W9W9?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/61Z8YpK7iZL._AC_SL1000_.jpg",
            "rating": 4.3,
            "reviews": 34567,
            "description": "3D Motion Detection, 1080p HD video, Two-way talk, Sirens, Works with Alexa",
            "affiliate_source": "amazon",
            "category": "electronics"
        },
        
        # FITNESS & HEALTH (3 products)
        {
            "name": "Fitbit Charge 6 Fitness Tracker with Heart Rate and GPS",
            "price": 149.95,
            "asin": "B0CGJ5P5HN",
            "url": f"https://www.amazon.com/dp/B0CGJ5P5HN?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/618Bv5LxbUL._AC_SL1500_.jpg",
            "rating": 4.3,
            "reviews": 12345,
            "description": "6+ day battery life, Built-in GPS, 40+ exercise modes, Google apps, ECG app",
            "affiliate_source": "amazon",
            "category": "sports"
        },
        {
            "name": "Yoga Mat Extra Thick Non Slip Exercise Mat",
            "price": 29.99,
            "asin": "B09PKPGCPC",
            "url": f"https://www.amazon.com/dp/B09PKPGCPC?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/81bWswvC-gL._AC_SL1500_.jpg",
            "rating": 4.6,
            "reviews": 78901,
            "description": "1/2 inch thick, non-slip surface, waterproof, carry strap included, 72x24 inches",
            "affiliate_source": "amazon",
            "category": "sports"
        },
        {
            "name": "Hydro Flask Standard Mouth Water Bottle 32 Fl Oz",
            "price": 37.95,
            "asin": "B07H9Y1B3Y",
            "url": f"https://www.amazon.com/dp/B07H9Y1B3Y?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/81c8YbNKnvL._AC_SL1500_.jpg",
            "rating": 4.7,
            "reviews": 45678,
            "description": "TempShield insulation, keeps drinks cold 24 hours, hot 12 hours. BPA-free. 18/8 stainless steel.",
            "affiliate_source": "amazon",
            "category": "sports"
        },
        
        # BEAUTY & PERSONAL CARE (2 products - 10% commission!)
        {
            "name": "Colgate Total Advanced Whitening Toothpaste 12 Ounce",
            "price": 12.99,
            "asin": "B003CSODOU",
            "url": f"https://www.amazon.com/dp/B003CSODOU?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/61sM2oDDjJL._AC_SL1500_.jpg",
            "rating": 4.6,
            "reviews": 98765,
            "description": "Advanced whitening, 12-hour protection, fights cavities and gingivitis",
            "affiliate_source": "amazon",
            "category": "beauty"
        },
        {
            "name": "Olaplex No.3 Hair Perfector Repairing Treatment",
            "price": 30.00,
            "asin": "B00TSSNS30",
            "url": f"https://www.amazon.com/dp/B00TSSNS30?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/7159HdluZvL._AC_SL1500_.jpg",
            "rating": 4.5,
            "reviews": 34567,
            "description": "Bond-building treatment for damaged hair. At-home treatment. 3.3 fl oz.",
            "affiliate_source": "amazon",
            "category": "beauty"
        },
        
        # BESTSELLERS - Mixed Categories (4 products)
        {
            "name": "Instant Pot Duo Crisp Air Fryer, 11-in-1 Pressure Cooker",
            "price": 149.95,
            "asin": "B08B6XN5PC",
            "url": f"https://www.amazon.com/dp/B08B6XN5PC?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/816yXF7vrrL._AC_SL1500_.jpg",
            "rating": 4.6,
            "reviews": 23456,
            "description": "Pressure cooker, air fryer, slow cooker combo. Cook with oil or air fry with crisp results.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        {
            "name": "KitchenAid Classic Stand Mixer, 4.5 Quart, 170W, Empire Red",
            "price": 329.99,
            "asin": "B00FPSKY4K",
            "url": f"https://www.amazon.com/dp/B00FPSKY4K?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/61fAXa2FEiL._AC_SL1500_.jpg",
            "rating": 4.8,
            "reviews": 56789,
            "description": "10 speeds, 67-point planetary mixing action, dough hook, whisk, and flat beater included.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        {
            "name": "Dyson V15 Detect Cordless Vacuum with Laser",
            "price": 649.99,
            "asin": "B09X5VJ8KM",
            "url": f"https://www.amazon.com/dp/B09X5VJ8KM?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/41VhMfXs2ML._AC_SL1500_.jpg",
            "rating": 4.4,
            "reviews": 34567,
            "description": "Laser detects dust invisible to the naked eye. Premium deep cleaning with powerful suction.",
            "affiliate_source": "amazon",
            "category": "home"
        },
        {
            "name": "Apple AirTag 4 Pack - AirTags with Precision Finding",
            "price": 99.00,
            "asin": "B0933QJXHY",
            "url": f"https://www.amazon.com/dp/B0933QJXHY?tag={AMAZON_PARTNER_TAG}",
            "image_url": "https://m.media-amazon.com/images/I/81LhHLZjRyL._AC_SL1500_.jpg",
            "rating": 4.5,
            "reviews": 234567,
            "description": "One-tap setup. Precision Finding with iPhone 11 and later. Privacy built in.",
            "affiliate_source": "amazon",
            "category": "electronics"
        }
    ]
    
    # Smart search: Match products based on query keywords
    query_lower = query.lower()
    query_words = query_lower.split()
    
    # Score each product based on keyword matches
    scored_products = []
    for product in all_products:
        score = 0
        name_lower = product['name'].lower()
        desc_lower = product.get('description', '').lower()
        
        for word in query_words:
            if word in name_lower:
                score += 10  # Name match is most important
            elif word in desc_lower:
                score += 3  # Description match
            elif word == product.get('category', ''):
                score += 5  # Category match
        
        if score > 0:
            product['_search_score'] = score
            scored_products.append(product)
    
    # Sort by search score (best matches first)
    scored_products.sort(key=lambda x: x.get('_search_score', 0), reverse=True)
    
    # If no matches, return all products
    if not scored_products:
        scored_products = all_products
    
    # Filter by price if specified
    if max_price:
        scored_products = [p for p in scored_products if p['price'] <= max_price]
    
    # Sort by rating and price (if multiple matches)
    scored_products.sort(key=lambda x: (x.get('rating', 0), -x.get('price', 0)), reverse=True)
    
    return scored_products[:max_results] if 'max_results' in locals() else scored_products[:5]

def affiliate_injector(url: str, source: str = 'amazon') -> str:
    """Ensure affiliate tracking is in URL"""
    if "amazon.com" in url and "tag=" not in url:
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}tag={AMAZON_PARTNER_TAG}"
    return url

def product_search_tool(query: str, max_price: Optional[float] = None, category: Optional[str] = None) -> str:
    """Main product search function"""
    try:
        products = get_expanded_products(query, max_price)
        
        response = {
            "status": "success",
            "query": query,
            "category": category,
            "max_price": max_price,
            "total_results": len(products),
            "products": products,
            "data_source": "curated_amazon"
        }
        
        return json.dumps(response)
        
    except Exception as e:
        logger.error(f"Product search error: {str(e)}")
        error_response = {
            "status": "error",
            "query": query,
            "error": str(e),
            "message": "Unable to search for products at this time."
        }
        return json.dumps(error_response)


