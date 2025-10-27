# lambda_ai_pro_complete_shopping.py
# AI Pro Complete Shopping Assistant - Full purchase flow with cart and checkout

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
    """Return APL document for product display with purchase options"""
    from lambda_ai_pro_shopping import get_shopping_apl_document
    
    # Use the enhanced APL document from file
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
                    "justifyContent": "spaceBetween",
                    "background": {
                        "type": "LinearGradient",
                        "colorRange": ["#0f0f23", "#1a1a2e", "#16213e"],
                        "inputRange": [0, 0.5, 1],
                        "angle": 135
                    },
                    "items": [
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingTop": 30,
                            "paddingLeft": 40,
                            "paddingRight": 40,
                            "paddingBottom": 20,
                            "items": [
                                {
                                    "type": "Text",
                                    "text": f"🛍️ Shopping Results: {query}",
                                    "fontSize": 26,
                                    "fontWeight": "bold",
                                    "color": "#00d4ff",
                                    "textAlign": "center"
                                }
                            ]
                        },
                        {
                            "type": "Sequence",
                            "width": "100%",
                            "height": "75vh",
                            "paddingLeft": 40,
                            "paddingRight": 40,
                            "scrollDirection": "vertical",
                            "data": "${payload.products}",
                            "numbered": True,
                            "items": [
                                {
                                    "type": "Container",
                                    "width": "100%",
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "borderRadius": 20,
                                    "borderWidth": 1,
                                    "borderColor": "rgba(255, 255, 255, 0.1)",
                                    "padding": 25,
                                    "marginBottom": 20,
                                    "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.3)",
                                    "items": [
                                        {
                                            "type": "Container",
                                            "direction": "row",
                                            "items": [
                                                {
                                                    "type": "Image",
                                                    "source": "${data.image_url}",
                                                    "width": 150,
                                                    "height": 150,
                                                    "scale": "best-fit",
                                                    "borderRadius": 15,
                                                    "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.3)"
                                                },
                                                {
                                                    "type": "Container",
                                                    "paddingLeft": 25,
                                                    "grow": 1,
                                                    "items": [
                                                        {
                                                            "type": "Text",
                                                            "text": "${data.name}",
                                                            "fontSize": 20,
                                                            "fontWeight": "bold",
                                                            "color": "#ffffff",
                                                            "maxLines": 2
                                                        },
                                                        {
                                                            "type": "Container",
                                                            "direction": "row",
                                                            "marginTop": 10,
                                                            "items": [
                                                                {
                                                                    "type": "Text",
                                                                    "text": "$${data.price}",
                                                                    "fontSize": 28,
                                                                    "fontWeight": "bold",
                                                                    "color": "#00ff88"
                                                                },
                                                                {
                                                                    "type": "Container",
                                                                    "paddingLeft": 20,
                                                                    "items": [
                                                                        {
                                                                            "type": "Text",
                                                                            "text": "⭐ ${data.rating}/5",
                                                                            "fontSize": 14,
                                                                            "color": "#ffd700"
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "type": "Text",
                                                            "text": "${data.description}",
                                                            "fontSize": 14,
                                                            "color": "#cbd5e0",
                                                            "maxLines": 2,
                                                            "marginTop": 10
                                                        },
                                                        {
                                                            "type": "Container",
                                                            "marginTop": 15,
                                                            "padding": 15,
                                                            "background": {
                                                                "type": "LinearGradient",
                                                                "colorRange": ["#00ff88", "#00cc66"],
                                                                "angle": 45
                                                            },
                                                            "borderRadius": 12,
                                                            "items": [
                                                                {
                                                                    "type": "Text",
                                                                    "text": "🛒 Say: Add item ${index+1}",
                                                                    "fontSize": 14,
                                                                    "fontWeight": "bold",
                                                                    "color": "#0f0f23",
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
            ]
        }
    }

def get_apl_document_cart(cart):
    """Return APL document for shopping cart view"""
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
                        "type": "LinearGradient",
                        "colorRange": ["#0f0f23", "#1a1a2e", "#16213e"],
                        "inputRange": [0, 0.5, 1],
                        "angle": 135
                    },
                    "items": [
                        {
                            "type": "Container",
                            "padding": 40,
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "🛒 Your Shopping Cart",
                                    "fontSize": 32,
                                    "fontWeight": "bold",
                                    "color": "#00d4ff",
                                    "marginBottom": 30
                                },
                                {
                                    "type": "Sequence",
                                    "height": "50vh",
                                    "data": "${payload.cartItems}",
                                    "items": [
                                        {
                                            "type": "Container",
                                            "width": "100%",
                                            "background": "rgba(0, 255, 136, 0.1)",
                                            "borderRadius": 15,
                                            "borderWidth": 2,
                                            "borderColor": "#00ff88",
                                            "padding": 20,
                                            "marginBottom": 15,
                                            "items": [
                                                {
                                                    "type": "Container",
                                                    "direction": "row",
                                                    "items": [
                                                        {
                                                            "type": "Image",
                                                            "source": "${data.image_url}",
                                                            "width": 80,
                                                            "height": 80,
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
                                                                    "color": "#ffffff"
                                                                },
                                                                {
                                                                    "type": "Text",
                                                                    "text": "$${data.price}",
                                                                    "fontSize": 22,
                                                                    "fontWeight": "bold",
                                                                    "color": "#00ff88",
                                                                    "marginTop": 5
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "Container",
                                    "marginTop": 30,
                                    "padding": 30,
                                    "background": "rgba(0, 212, 255, 0.1)",
                                    "borderRadius": 20,
                                    "borderWidth": 2,
                                    "borderColor": "#00d4ff",
                                    "items": [
                                        {
                                            "type": "Container",
                                            "direction": "row",
                                            "justifyContent": "spaceBetween",
                                            "items": [
                                                {
                                                    "type": "Text",
                                                    "text": "Total:",
                                                    "fontSize": 26,
                                                    "fontWeight": "bold",
                                                    "color": "#ffffff"
                                                },
                                                {
                                                    "type": "Text",
                                                    "text": "$${payload.cartTotal}",
                                                    "fontSize": 36,
                                                    "fontWeight": "bold",
                                                    "color": "#00ff88"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "Container",
                                            "marginTop": 20,
                                            "padding": 20,
                                            "background": {
                                                "type": "LinearGradient",
                                                "colorRange": ["#00d4ff", "#0099cc"],
                                                "angle": 45
                                            },
                                            "borderRadius": 15,
                                            "items": [
                                                {
                                                    "type": "Text",
                                                    "text": "💳 Say: Checkout now",
                                                    "fontSize": 20,
                                                    "fontWeight": "bold",
                                                    "color": "#0f0f23",
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
    }

def get_apl_document_confirmation(order):
    """Return APL document for order confirmation"""
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
                    "alignItems": "center",
                    "justifyContent": "center",
                    "background": {
                        "type": "LinearGradient",
                        "colorRange": ["#0f0f23", "#1a1a2e", "#16213e"],
                        "inputRange": [0, 0.5, 1],
                        "angle": 135
                    },
                    "items": [
                        {
                            "type": "Container",
                            "width": "70%",
                            "padding": 50,
                            "background": "rgba(0, 255, 136, 0.1)",
                            "borderRadius": 30,
                            "borderWidth": 3,
                            "borderColor": "#00ff88",
                            "boxShadow": "0 10px 50px rgba(0, 255, 136, 0.3)",
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "✅",
                                    "fontSize": 100,
                                    "textAlign": "center",
                                    "marginBottom": 20
                                },
                                {
                                    "type": "Text",
                                    "text": "Order Confirmed!",
                                    "fontSize": 42,
                                    "fontWeight": "bold",
                                    "color": "#00ff88",
                                    "textAlign": "center",
                                    "marginBottom": 30
                                },
                                {
                                    "type": "Text",
                                    "text": "Order #${payload.orderId}",
                                    "fontSize": 24,
                                    "color": "#ffffff",
                                    "textAlign": "center",
                                    "marginBottom": 20
                                },
                                {
                                    "type": "Container",
                                    "direction": "row",
                                    "justifyContent": "spaceBetween",
                                    "width": "100%",
                                    "marginBottom": 30,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Total Paid:",
                                            "fontSize": 20,
                                            "color": "#cbd5e0"
                                        },
                                        {
                                            "type": "Text",
                                            "text": "$${payload.orderTotal}",
                                            "fontSize": 28,
                                            "fontWeight": "bold",
                                            "color": "#00ff88"
                                        }
                                    ]
                                },
                                {
                                    "type": "Text",
                                    "text": "Tracking: ${payload.trackingNumber}",
                                    "fontSize": 16,
                                    "color": "#00d4ff",
                                    "textAlign": "center",
                                    "marginBottom": 10
                                },
                                {
                                    "type": "Text",
                                    "text": "Estimated Delivery: ${payload.delivery}",
                                    "fontSize": 14,
                                    "color": "#a0a0a0",
                                    "textAlign": "center",
                                    "marginBottom": 30
                                },
                                {
                                    "type": "Text",
                                    "text": "Check your Alexa app for order details and tracking information.",
                                    "fontSize": 14,
                                    "color": "#a0a0a0",
                                    "textAlign": "center",
                                    "fontStyle": "italic"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }

def lambda_handler(event, context):
    """Enhanced Lambda function with complete shopping cart and checkout flow"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract user ID and session
        user_id = event['session']['user']['userId']
        request_type = event['request']['type']
        session_attributes = event['session'].get('attributes', {})
        
        logger.info(f"User: {user_id}, Request Type: {request_type}")
        
        # Handle different request types
        if request_type == 'LaunchRequest':
            response_text = "Welcome to AI Pro Shopping! I can help you find products, manage your cart, and complete purchases. What would you like to shop for today?"
            
            return {
                'version': '1.0',
                'sessionAttributes': session_attributes,
                'response': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': response_text
                    },
                    'shouldEndSession': False
                }
            }
        
        elif request_type == 'IntentRequest':
            intent_name = event['request']['intent']['name']
            logger.info(f"Intent: {intent_name}")
            
            # ========== SHOPPING SEARCH ==========
            if intent_name == 'ShoppingIntent' or intent_name == 'LLMQueryIntent':
                # Extract query parameters
                slots = event['request']['intent'].get('slots', {})
                
                if intent_name == 'ShoppingIntent':
                    product = slots.get('Product', {}).get('value', '')
                    price = slots.get('Price', {}).get('value', '')
                    category = slots.get('Category', {}).get('value', '')
                else:
                    query_slot = slots.get('Query', {})
                    product = query_slot.get('value', '')
                    price = slots.get('Price', {}).get('value', '')
                    category = ''
                
                logger.info(f"Shopping search: {product}, Price: {price}, Category: {category}")
                
                try:
                    max_price = float(price) if price else None
                    
                    # Call product search
                    tool_output = product_search_tool(product, max_price, category)
                    tool_data = json.loads(tool_output)
                    
                    if tool_data.get('status') == 'success':
                        products = tool_data.get('products', [])
                        
                        if products:
                            # Store products in session for later reference
                            session_attributes['current_products'] = json.dumps(products)
                            
                            # Voice response
                            response_text = f"I found {len(products)} great options for you. "
                            for i, p in enumerate(products[:3], 1):
                                response_text += f"Item {i}: {p['name']} at ${p['price']:.2f}. "
                            response_text += "You can say 'add item 1' to add any item to your cart, or 'view cart' to see what you have."
                            
                            # Build response with APL
                            return {
                                'version': '1.0',
                                'sessionAttributes': session_attributes,
                                'response': {
                                    'outputSpeech': {
                                        'type': 'SSML',
                                        'ssml': f'<speak>{response_text}</speak>'
                                    },
                                    'card': {
                                        'type': 'Standard',
                                        'title': f"Shopping Results: {product}",
                                        'text': f"Found {len(products)} products. Check your screen or Alexa app for details.",
                                        'image': {
                                            'largeImageUrl': products[0].get('image_url', '')
                                        }
                                    },
                                    'directives': [
                                        {
                                            'type': 'Alexa.Presentation.APL.RenderDocument',
                                            'token': 'shopping-products',
                                            'document': get_apl_document_products(products, product),
                                            'datasources': {
                                                'payload': {
                                                    'products': products,
                                                    'query': product
                                                }
                                            }
                                        }
                                    ],
                                    'shouldEndSession': False
                                }
                            }
                        else:
                            response_text = f"I couldn't find any products matching '{product}'. Try being more specific or adjusting your criteria."
                    else:
                        response_text = "I'm having trouble searching for products right now. Please try again."
                        
                except Exception as e:
                    logger.error(f"Shopping search error: {str(e)}")
                    response_text = f"I encountered an error searching for products: {str(e)}"
            
            # ========== ADD TO CART ==========
            elif intent_name == 'AddToCartIntent':
                slots = event['request']['intent'].get('slots', {})
                item_number = slots.get('ItemNumber', {}).get('value', '')
                
                if item_number and 'current_products' in session_attributes:
                    try:
                        item_index = int(item_number) - 1
                        products = json.loads(session_attributes['current_products'])
                        
                        if 0 <= item_index < len(products):
                            product = products[item_index]
                            cart, added = add_to_cart(user_id, product)
                            
                            if added:
                                response_text = f"Added {product['name']} to your cart for ${product['price']:.2f}. You now have {len(cart['items'])} items. Say 'view cart' to review, or keep shopping!"
                            else:
                                response_text = f"That item is already in your cart! Say 'view cart' to see all your items."
                        else:
                            response_text = f"I don't see item {item_number} in the results. Please choose a valid item number."
                    except Exception as e:
                        logger.error(f"Add to cart error: {str(e)}")
                        response_text = "Sorry, I couldn't add that item to your cart. Please try again."
                else:
                    response_text = "Please search for products first before adding items to your cart."
            
            # ========== VIEW CART ==========
            elif intent_name == 'ViewCartIntent':
                cart = get_user_cart(user_id)
                
                if cart['items']:
                    response_text = f"You have {len(cart['items'])} items in your cart totaling ${cart['total']:.2f}. "
                    for i, item in enumerate(cart['items'], 1):
                        response_text += f"Item {i}: {item['name']} at ${item['price']:.2f}. "
                    response_text += "Say 'checkout now' to complete your purchase, or 'clear cart' to start over."
                    
                    # Return cart APL view
                    return {
                        'version': '1.0',
                        'sessionAttributes': session_attributes,
                        'response': {
                            'outputSpeech': {
                                'type': 'SSML',
                                'ssml': f'<speak>{response_text}</speak>'
                            },
                            'directives': [
                                {
                                    'type': 'Alexa.Presentation.APL.RenderDocument',
                                    'token': 'shopping-cart',
                                    'document': get_apl_document_cart(cart),
                                    'datasources': {
                                        'payload': {
                                            'cartItems': cart['items'],
                                            'cartTotal': f"{cart['total']:.2f}"
                                        }
                                    }
                                }
                            ],
                            'shouldEndSession': False
                        }
                    }
                else:
                    response_text = "Your cart is empty. Search for products to start shopping!"
            
            # ========== CHECKOUT ==========
            elif intent_name == 'CheckoutIntent':
                cart = get_user_cart(user_id)
                
                if cart['items']:
                    # Ask for confirmation
                    session_attributes['pending_checkout'] = 'true'
                    response_text = f"You're about to purchase {len(cart['items'])} items for a total of ${cart['total']:.2f}. Say 'yes, buy it' to confirm, or 'cancel' to go back."
                else:
                    response_text = "Your cart is empty. Add some items before checking out!"
            
            # ========== CONFIRM PURCHASE ==========
            elif intent_name == 'ConfirmPurchaseIntent' or intent_name == 'AMAZON.YesIntent':
                if session_attributes.get('pending_checkout') == 'true':
                    cart = get_user_cart(user_id)
                    
                    if cart['items']:
                        # Create order
                        order = create_order(user_id, cart)
                        
                        if order:
                            # Clear cart after successful order
                            clear_cart(user_id)
                            session_attributes['pending_checkout'] = 'false'
                            
                            response_text = f"Order confirmed! Your order number is {order['order_id']}. Total: ${order['total']:.2f}. You'll receive confirmation details in your Alexa app. Estimated delivery in {order['estimated_delivery']}."
                            
                            # Return confirmation APL
                            return {
                                'version': '1.0',
                                'sessionAttributes': session_attributes,
                                'response': {
                                    'outputSpeech': {
                                        'type': 'SSML',
                                        'ssml': f'<speak>{response_text}</speak>'
                                    },
                                    'card': {
                                        'type': 'Standard',
                                        'title': f"Order Confirmed - #{order['order_id']}",
                                        'text': f"Total: ${order['total']:.2f}\\nTracking: {order['tracking_number']}\\nDelivery: {order['estimated_delivery']}"
                                    },
                                    'directives': [
                                        {
                                            'type': 'Alexa.Presentation.APL.RenderDocument',
                                            'token': 'order-confirmation',
                                            'document': get_apl_document_confirmation(order),
                                            'datasources': {
                                                'payload': {
                                                    'orderId': order['order_id'],
                                                    'orderTotal': f"{order['total']:.2f}",
                                                    'trackingNumber': order['tracking_number'],
                                                    'delivery': order['estimated_delivery']
                                                }
                                            }
                                        }
                                    ],
                                    'shouldEndSession': False
                                }
                            }
                        else:
                            response_text = "Sorry, there was an error processing your order. Please try again."
                    else:
                        response_text = "Your cart is empty. Nothing to check out!"
                else:
                    response_text = "I'm not sure what you're confirming. Say 'checkout' to review your cart first."
            
            # ========== CANCEL PURCHASE ==========
            elif intent_name == 'CancelPurchaseIntent' or intent_name == 'AMAZON.NoIntent':
                if session_attributes.get('pending_checkout') == 'true':
                    session_attributes['pending_checkout'] = 'false'
                    response_text = "Checkout cancelled. Your items are still in your cart. Say 'view cart' to review, or keep shopping!"
                else:
                    response_text = "Okay, what would you like to do?"
            
            # ========== REMOVE FROM CART ==========
            elif intent_name == 'RemoveFromCartIntent':
                slots = event['request']['intent'].get('slots', {})
                item_number = slots.get('ItemNumber', {}).get('value', '')
                
                if item_number:
                    try:
                        item_index = int(item_number) - 1
                        cart, removed_item = remove_from_cart(user_id, item_index)
                        
                        if removed_item:
                            response_text = f"Removed {removed_item['name']} from your cart. You now have {len(cart['items'])} items."
                        else:
                            response_text = f"I couldn't find item {item_number} in your cart."
                    except Exception as e:
                        logger.error(f"Remove from cart error: {str(e)}")
                        response_text = "Sorry, I couldn't remove that item. Please try again."
                else:
                    response_text = "Which item number would you like to remove?"
            
            # ========== CLEAR CART ==========
            elif intent_name == 'ClearCartIntent':
                clear_cart(user_id)
                response_text = "Your cart has been cleared. Ready to start fresh!"
            
            # ========== HELP ==========
            elif intent_name == 'AMAZON.HelpIntent':
                response_text = "I can help you shop! Try saying: 'Find me headphones', 'Show my cart', 'Add item 1', or 'Checkout now'. What would you like to do?"
            
            # ========== STOP/CANCEL ==========
            elif intent_name in ['AMAZON.StopIntent', 'AMAZON.CancelIntent']:
                response_text = "Thanks for shopping with AI Pro! Goodbye!"
                
                return {
                    'version': '1.0',
                    'sessionAttributes': session_attributes,
                    'response': {
                        'outputSpeech': {
                            'type': 'PlainText',
                            'text': response_text
                        },
                        'shouldEndSession': True
                    }
                }
            
            else:
                response_text = "I didn't understand that. Try saying 'help' for instructions."
        
        else:
            response_text = "I didn't understand that request."
        
        # Default response
        return {
            'version': '1.0',
            'sessionAttributes': session_attributes,
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': response_text
                },
                'shouldEndSession': False
            }
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': 'Sorry, I encountered an error. Please try again.'
                },
                'shouldEndSession': False
            }
        }

