# lambda_ai_pro_complete_shopping.py
# AI Pro Complete Shopping Assistant - Full purchase flow with beautiful APL design

import json
import boto3
import os
import logging
import urllib.request
import urllib.parse
import uuid
from datetime import datetime
from decimal import Decimal
from shopping_tools import product_search_tool, affiliate_injector

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'ai-assistant-users-dev'))

# Shopping cart and order management
def get_user_cart(user_id):
    """Retrieve user's shopping cart from DynamoDB"""
    try:
        response = users_table.get_item(Key={'userId': user_id})
        if 'Item' in response and 'shopping_cart' in response['Item']:
            cart_data = response['Item']['shopping_cart']
            # Handle DynamoDB format
            if isinstance(cart_data, str):
                return json.loads(cart_data)
            return cart_data
        return {'items': [], 'total': 0.0}
    except Exception as e:
        logger.error(f"Error retrieving cart: {str(e)}")
        return {'items': [], 'total': 0.0}

def save_user_cart(user_id, cart):
    """Save user's shopping cart to DynamoDB"""
    try:
        users_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='SET shopping_cart = :cart, last_updated = :timestamp',
            ExpressionAttributeValues={
                ':cart': json.dumps(cart),
                ':timestamp': datetime.now().isoformat()
            }
        )
        logger.info(f"Cart saved for user {user_id}: {len(cart.get('items', []))} items")
        return True
    except Exception as e:
        logger.error(f"Error saving cart: {str(e)}")
        return False

def add_to_cart(user_id, product):
    """Add a product to user's cart"""
    cart = get_user_cart(user_id)
    
    # Check if product already in cart
    for item in cart['items']:
        if item.get('url') == product.get('url'):
            logger.info(f"Product already in cart: {product['name']}")
            return cart, False  # Already in cart
    
    # Add product to cart
    cart['items'].append(product)
    cart['total'] = sum(item.get('price', 0) for item in cart['items'])
    
    save_user_cart(user_id, cart)
    return cart, True

def remove_from_cart(user_id, item_index):
    """Remove a product from user's cart"""
    cart = get_user_cart(user_id)
    
    if 0 <= item_index < len(cart['items']):
        removed_item = cart['items'].pop(item_index)
        cart['total'] = sum(item.get('price', 0) for item in cart['items'])
        save_user_cart(user_id, cart)
        return cart, removed_item
    
    return cart, None

def clear_cart(user_id):
    """Clear all items from user's cart"""
    cart = {'items': [], 'total': 0.0}
    save_user_cart(user_id, cart)
    return cart

def create_order(user_id, cart):
    """Create an order from cart items"""
    order_id = str(uuid.uuid4())[:8].upper()
    
    order = {
        'order_id': order_id,
        'user_id': user_id,
        'items': cart['items'],
        'total': cart['total'],
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'tracking_number': f"AIPRO-{order_id}",
        'estimated_delivery': '3-5 business days'
    }
    
    try:
        # Save order to DynamoDB
        users_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='SET last_order = :order, order_history = list_append(if_not_exists(order_history, :empty_list), :new_order)',
            ExpressionAttributeValues={
                ':order': json.dumps(order),
                ':new_order': [json.dumps(order)],
                ':empty_list': []
            }
        )
        
        logger.info(f"Order created: {order_id} for user {user_id}")
        return order
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return None


def get_apl_document_products(products, query):
    """
    Beautiful, responsive product listing APL.
    Optimized for both Echo Show (large) and Echo Spot (small) screens.
    Features:
    - Modern gradient header with search query
    - Clean product cards with images, names, prices, ratings
    - Responsive layout that adapts to screen size
    - Clear call-to-action for adding items
    """
    logger.info(f"GENERATING BEAUTIFUL APL for query: {query}")
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
                    "background": "#ffffff",
                    "items": [
                        # Header with gradient background
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingTop": 16,
                            "paddingBottom": 16,
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "background": {
                                "type": "LinearGradient",
                                "colorRange": ["#667eea", "#764ba2"],
                                "angle": 135
                            },
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "Search Results",
                                    "fontSize": 14,
                                    "fontWeight": "300",
                                    "color": "rgba(255, 255, 255, 0.8)"
                                },
                                {
                                    "type": "Text",
                                    "text": f"{query}",
                                    "fontSize": 28,
                                    "fontWeight": "bold",
                                    "color": "#ffffff",
                                    "marginTop": 4
                                }
                            ]
                        },
                        # Product count indicator
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "paddingTop": 12,
                            "paddingBottom": 12,
                            "background": "#f7fafc",
                            "items": [
                                {
                                    "type": "Text",
                                    "text": f"{len(products)} products found",
                                    "fontSize": 12,
                                    "color": "#718096",
                                    "fontWeight": "500"
                                }
                            ]
                        },
                        # Product list with scroll
                        {
                            "type": "Sequence",
                            "width": "100%",
                            "height": "1fr",
                            "scrollDirection": "vertical",
                            "data": "${payload.products}",
                            "numbered": False,
                            "items": [
                                {
                                    "type": "Container",
                                    "width": "100%",
                                    "paddingLeft": 16,
                                    "paddingRight": 16,
                                    "paddingTop": 12,
                                    "paddingBottom": 12,
                                    "items": [
                                        {
                                            "type": "Container",
                                            "width": "100%",
                                            "background": "#ffffff",
                                            "borderRadius": 12,
                                            "paddingLeft": 16,
                                            "paddingRight": 16,
                                            "paddingTop": 16,
                                            "paddingBottom": 16,
                                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.08)",
                                            "items": [
                                                # Product image and info row
                                                {
                                                    "type": "Container",
                                                    "direction": "row",
                                                    "items": [
                                                        # Product image
                                                        {
                                                            "type": "Image",
                                                            "source": "${data.image_url}",
                                                            "width": 120,
                                                            "height": 120,
                                                            "scale": "best-fit",
                                                            "borderRadius": 8,
                                                            "boxShadow": "0 2px 6px rgba(0, 0, 0, 0.1)"
                                                        },
                                                        # Product details
                                                        {
                                                            "type": "Container",
                                                            "direction": "column",
                                                            "paddingLeft": 16,
                                                            "grow": 1,
                                                            "items": [
                                                                # Product name
                                                                {
                                                                    "type": "Text",
                                                                    "text": "${data.name}",
                                                                    "fontSize": 16,
                                                                    "fontWeight": "bold",
                                                                    "color": "#2d3748",
                                                                    "maxLines": 2
                                                                },
                                                                # Price and rating row
                                                                {
                                                                    "type": "Container",
                                                                    "direction": "row",
                                                                    "marginTop": 8,
                                                                    "alignItems": "center",
                                                                    "items": [
                                                                        # Price
                                                                        {
                                                                            "type": "Text",
                                                                            "text": "$${data.price}",
                                                                            "fontSize": 20,
                                                                            "fontWeight": "bold",
                                                                            "color": "#48bb78"
                                                                        },
                                                                        # Rating
                                                                        {
                                                                            "type": "Text",
                                                                            "text": "⭐ ${data.rating}",
                                                                            "fontSize": 12,
                                                                            "color": "#f6ad55",
                                                                            "marginLeft": 12
                                                                        }
                                                                    ]
                                                                },
                                                                # Description
                                                                {
                                                                    "type": "Text",
                                                                    "text": "${data.description}",
                                                                    "fontSize": 12,
                                                                    "color": "#718096",
                                                                    "maxLines": 2,
                                                                    "marginTop": 8
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                },
                                                # Action button
                                                {
                                                    "type": "Container",
                                                    "width": "100%",
                                                    "marginTop": 12,
                                                    "paddingTop": 12,
                                                    "borderTopWidth": 1,
                                                    "borderTopColor": "#e2e8f0",
                                                    "items": [
                                                        {
                                                            "type": "Text",
                                                            "text": "Say: Add item ${index+1}",
                                                            "fontSize": 12,
                                                            "color": "#667eea",
                                                            "fontWeight": "bold",
                                                            "textAlign": "center"
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
            ]
        }
    }


def get_apl_document_cart(cart):
    """
    Beautiful shopping cart APL.
    Shows all items with total and checkout prompt.
    Responsive design for all Alexa devices.
    """
    logger.info(f"GENERATING BEAUTIFUL CART APL with {len(cart.get('items', []))} items")
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
                    "background": "#ffffff",
                    "items": [
                        # Header
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingTop": 16,
                            "paddingBottom": 16,
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "background": {
                                "type": "LinearGradient",
                                "colorRange": ["#667eea", "#764ba2"],
                                "angle": 135
                            },
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "Your Shopping Cart",
                                    "fontSize": 28,
                                    "fontWeight": "bold",
                                    "color": "#ffffff"
                                }
                            ]
                        },
                        # Cart items
                        {
                            "type": "Sequence",
                            "width": "100%",
                            "height": "1fr",
                            "scrollDirection": "vertical",
                            "data": "${payload.cartItems}",
                            "numbered": True,
                            "items": [
                                {
                                    "type": "Container",
                                    "width": "100%",
                                    "paddingLeft": 16,
                                    "paddingRight": 16,
                                    "paddingTop": 12,
                                    "paddingBottom": 12,
                                    "items": [
                                        {
                                            "type": "Container",
                                            "width": "100%",
                                            "background": "#f7fafc",
                                            "borderRadius": 8,
                                            "padding": 12,
                                            "items": [
                                                {
                                                    "type": "Container",
                                                    "direction": "row",
                                                    "items": [
                                                        {
                                                            "type": "Text",
                                                            "text": "${index+1}",
                                                            "fontSize": 14,
                                                            "fontWeight": "bold",
                                                            "color": "#667eea",
                                                            "marginRight": 12
                                                        },
                                                        {
                                                            "type": "Container",
                                                            "direction": "column",
                                                            "grow": 1,
                                                            "items": [
                                                                {
                                                                    "type": "Text",
                                                                    "text": "${data.name}",
                                                                    "fontSize": 14,
                                                                    "fontWeight": "bold",
                                                                    "color": "#2d3748"
                                                                },
                                                                {
                                                                    "type": "Text",
                                                                    "text": "$${data.price}",
                                                                    "fontSize": 12,
                                                                    "color": "#48bb78",
                                                                    "marginTop": 4
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
                        },
                        # Cart total and checkout
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingLeft": 16,
                            "paddingRight": 16,
                            "paddingTop": 16,
                            "paddingBottom": 16,
                            "background": "#f7fafc",
                            "items": [
                                {
                                    "type": "Container",
                                    "direction": "row",
                                    "marginBottom": 16,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Total:",
                                            "fontSize": 18,
                                            "fontWeight": "bold",
                                            "color": "#2d3748"
                                        },
                                        {
                                            "type": "Text",
                                            "text": "$${payload.cartTotal}",
                                            "fontSize": 24,
                                            "fontWeight": "bold",
                                            "color": "#48bb78",
                                            "grow": 1,
                                            "textAlign": "right"
                                        }
                                    ]
                                },
                                {
                                    "type": "Container",
                                    "width": "100%",
                                    "background": {
                                        "type": "LinearGradient",
                                        "colorRange": ["#667eea", "#764ba2"],
                                        "angle": 135
                                    },
                                    "borderRadius": 8,
                                    "padding": 12,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Say: Checkout now",
                                            "fontSize": 14,
                                            "fontWeight": "bold",
                                            "color": "#ffffff",
                                            "textAlign": "center"
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


def get_apl_document_checkout(order):
    """
    Beautiful order confirmation APL.
    Shows order details and next steps.
    """
    logger.info(f"GENERATING BEAUTIFUL CHECKOUT APL for order: {order.get('order_id')}")
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
                    "background": "#ffffff",
                    "items": [
                        # Success header
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingTop": 24,
                            "paddingBottom": 24,
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "background": {
                                "type": "LinearGradient",
                                "colorRange": ["#48bb78", "#38a169"],
                                "angle": 135
                            },
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "Order Confirmed!",
                                    "fontSize": 28,
                                    "fontWeight": "bold",
                                    "color": "#ffffff",
                                    "textAlign": "center"
                                }
                            ]
                        },
                        # Order details
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "paddingTop": 24,
                            "paddingBottom": 24,
                            "items": [
                                # Order number
                                {
                                    "type": "Container",
                                    "marginBottom": 20,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Order Number",
                                            "fontSize": 12,
                                            "color": "#718096",
                                            "fontWeight": "500"
                                        },
                                        {
                                            "type": "Text",
                                            "text": f"{order.get('order_id', 'N/A')}",
                                            "fontSize": 20,
                                            "fontWeight": "bold",
                                            "color": "#2d3748",
                                            "marginTop": 4
                                        }
                                    ]
                                },
                                # Total amount
                                {
                                    "type": "Container",
                                    "marginBottom": 20,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Total Amount",
                                            "fontSize": 12,
                                            "color": "#718096",
                                            "fontWeight": "500"
                                        },
                                        {
                                            "type": "Text",
                                            "text": f"${order.get('total', 0):.2f}",
                                            "fontSize": 28,
                                            "fontWeight": "bold",
                                            "color": "#48bb78",
                                            "marginTop": 4
                                        }
                                    ]
                                },
                                # Estimated delivery
                                {
                                    "type": "Container",
                                    "marginBottom": 20,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Estimated Delivery",
                                            "fontSize": 12,
                                            "color": "#718096",
                                            "fontWeight": "500"
                                        },
                                        {
                                            "type": "Text",
                                            "text": f"{order.get('estimated_delivery', 'N/A')}",
                                            "fontSize": 16,
                                            "color": "#2d3748",
                                            "marginTop": 4
                                        }
                                    ]
                                }
                            ]
                        },
                        # Next steps
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "paddingTop": 16,
                            "paddingBottom": 16,
                            "background": "#f7fafc",
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "Next Steps",
                                    "fontSize": 14,
                                    "fontWeight": "bold",
                                    "color": "#2d3748",
                                    "marginBottom": 12
                                },
                                {
                                    "type": "Text",
                                    "text": "Check your Alexa app for order details, tracking information, and delivery updates.",
                                    "fontSize": 12,
                                    "color": "#718096",
                                    "lineHeight": 1.6
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
