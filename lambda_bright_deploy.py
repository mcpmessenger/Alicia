# lambda_bright_deploy.py
# Updated Lambda function with BRIGHT MODE APL for deployment
# This fixes the dark display bug on physical Alexa devices

import json
import boto3
import os
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Simulated product catalog
PRODUCT_CATALOG = [
    {"id": 1, "name": "Wireless Bluetooth Headphones", "price": 79.99, "rating": 4.5, "reviews": 2341, "description": "Premium sound quality with 30-hour battery life", "image_url": "https://m.media-amazon.com/images/I/61eRjwzQzDL._AC_SL1500_.jpg"},
    {"id": 2, "name": "Smart Watch Fitness Tracker", "price": 149.99, "rating": 4.3, "reviews": 1876, "description": "Track your fitness goals with style", "image_url": "https://m.media-amazon.com/images/I/61ZjlBOp+rL._AC_SL1500_.jpg"},
    {"id": 3, "name": "Portable Power Bank 20000mAh", "price": 39.99, "rating": 4.7, "reviews": 3421, "description": "Fast charging for all your devices", "image_url": "https://m.media-amazon.com/images/I/61gO1U3EFEL._AC_SL1500_.jpg"},
    {"id": 4, "name": "Wireless Charging Pad", "price": 24.99, "rating": 4.4, "reviews": 1567, "description": "Convenient wireless charging for smartphones", "image_url": "https://m.media-amazon.com/images/I/61tP8KXRgIL._AC_SL1500_.jpg"},
    {"id": 5, "name": "USB-C Hub Adapter", "price": 34.99, "rating": 4.6, "reviews": 987, "description": "Expand your laptop connectivity", "image_url": "https://m.media-amazon.com/images/I/61vY3RXJbWL._AC_SL1500_.jpg"}
]

def search_products(query):
    """Search products based on query"""
    query_lower = query.lower()
    results = []
    
    for product in PRODUCT_CATALOG:
        if (query_lower in product['name'].lower() or 
            query_lower in product['description'].lower()):
            results.append(product)
    
    # Return top 3 results, or all products if no specific match
    if results:
        return results[:3]
    return PRODUCT_CATALOG[:3]

def get_bright_apl_products(products, query):
    """Return BRIGHT MODE APL document for product display"""
    return {
        "type": "APL",
        "version": "2023.3",
        "mainTemplate": {
            "parameters": ["payload"],
            "items": [
                {
                    "type": "Container",
                    "width": "100vw",
                    "height": "100vh",
                    "direction": "column",
                    "background": {
                        "color": "#FFFFFF"  # BRIGHT WHITE BACKGROUND
                    },
                    "items": [
                        {
                            "type": "Container",
                            "width": "100%",
                            "height": 80,
                            "background": "#667eea",
                            "padding": 20,
                            "items": [
                                {
                                    "type": "Text",
                                    "text": f"🛍️ Shopping: {query}",
                                    "fontSize": 28,
                                    "fontWeight": "bold",
                                    "color": "#ffffff",
                                    "textAlign": "center"
                                }
                            ]
                        },
                        {
                            "type": "Sequence",
                            "width": "100%",
                            "height": "80vh",
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "paddingTop": 20,
                            "data": "${payload.products}",
                            "numbered": True,
                            "items": [
                                {
                                    "type": "Container",
                                    "width": "100%",
                                    "background": "#f7fafc",  # Light gray card
                                    "borderRadius": 15,
                                    "padding": 20,
                                    "marginBottom": 15,
                                    "direction": "row",
                                    "items": [
                                        {
                                            "type": "Image",
                                            "source": "${data.image_url}",
                                            "width": 120,
                                            "height": 120,
                                            "scale": "best-fit",
                                            "borderRadius": 10
                                        },
                                        {
                                            "type": "Container",
                                            "paddingLeft": 20,
                                            "grow": 1,
                                            "items": [
                                                {
                                                    "type": "Text",
                                                    "text": "${data.name}",
                                                    "fontSize": 18,
                                                    "fontWeight": "bold",
                                                    "color": "#2d3748",  # Dark text
                                                    "maxLines": 2
                                                },
                                                {
                                                    "type": "Text",
                                                    "text": "$${data.price}",
                                                    "fontSize": 24,
                                                    "fontWeight": "bold",
                                                    "color": "#48bb78",  # Green price
                                                    "marginTop": 5
                                                },
                                                {
                                                    "type": "Text",
                                                    "text": "⭐ ${data.rating}/5 (${data.reviews} reviews)",
                                                    "fontSize": 13,
                                                    "color": "#718096",  # Gray text
                                                    "marginTop": 5
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }

def lambda_handler(event, context):
    """Main Lambda handler with BRIGHT MODE APL"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        user_id = event['session']['user']['userId']
        request_type = event['request']['type']
        
        # Check if device supports display
        supports_display = 'Display' in event['context']['System']['device'].get('supportedInterfaces', {})
        
        if request_type == 'LaunchRequest':
            response_text = "Welcome to AI Pro Shopping! Say 'show me headphones' or 'find smart watches' to start shopping."
            
        elif request_type == 'IntentRequest':
            intent_name = event['request']['intent']['name']
            
            if intent_name == 'ShoppingIntent':
                # Handle shopping queries
                query = event['request']['intent']['slots']['Query']['value']
                products = search_products(query)
                
                if products:
                    product_names = ", ".join([p['name'] for p in products[:2]])
                    response_text = f"I found {len(products)} products for {query}. Check your screen! I'm showing {product_names} and more."
                    
                    # Return response with BRIGHT APL
                    return {
                        'version': '1.0',
                        'response': {
                            'outputSpeech': {
                                'type': 'PlainText',
                                'text': response_text
                            },
                            'directives': [
                                {
                                    'type': 'Alexa.Presentation.APL.RenderDocument',
                                    'token': 'shopping-results',
                                    'document': get_bright_apl_products(products, query),
                                    'datasources': {
                                        'payload': {
                                            'products': products
                                        }
                                    }
                                }
                            ] if supports_display else [],
                            'shouldEndSession': False
                        }
                    }
                else:
                    response_text = f"Sorry, I couldn't find any products for {query}. Try searching for headphones, watches, or chargers."
            
            elif intent_name == 'AMAZON.HelpIntent':
                response_text = "Say 'show me headphones' or 'find smart watches' to start shopping!"
                
            else:
                response_text = "Say 'show me headphones' to start shopping!"
        
        else:
            response_text = "Welcome to AI Pro Shopping!"
        
        # Return basic response
        return {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': response_text
                },
                'shouldEndSession': False
            }
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': 'Sorry, I encountered an error.'
                },
                'shouldEndSession': False
            }
        }


