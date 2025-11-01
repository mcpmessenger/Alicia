# lambda_ai_pro_general.py
# AI Pro - Friendly General AI Assistant with Shopping Capabilities

import json
import boto3
import os
import logging
import urllib.request
import urllib.parse
import uuid
import random
from datetime import datetime
from decimal import Decimal
from shopping_tools import product_search_tool, affiliate_injector

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'ai-assistant-users-dev'))

# LLM Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

# Welcome messages (randomized for friendliness)
WELCOME_MESSAGES = [
    "Hi! I'm AI Pro. Ask me anything or tell me what you're looking for!",
    "Hey there! What's on your mind today?",
    "Hello! I'm here to help. What would you like to know or find?",
    "Hi! How can I help you today?",
    "Hey! What can I do for you?"
]

# Shopping keywords for intent detection
SHOPPING_KEYWORDS = [
    'buy', 'purchase', 'shop', 'shopping', 'find product', 'looking for', 
    'need', 'want to buy', 'show me', 'search for', 'find me', 'get me',
    'price', 'cost', 'deal', 'sale', 'discount', 'cheap', 'best'
]

CART_KEYWORDS = [
    'cart', 'checkout', 'my order', 'purchased', 'bought', 'add item',
    'remove item', 'clear cart', 'view cart', 'show cart', 'in my cart'
]

def detect_intent(text):
    """
    Smart intent detection: chat vs shopping vs cart management
    Returns: 'shopping', 'cart', or 'chat'
    """
    text_lower = text.lower()
    
    # Check for cart keywords first (more specific)
    if any(keyword in text_lower for keyword in CART_KEYWORDS):
        return 'cart'
    
    # Check for shopping keywords
    if any(keyword in text_lower for keyword in SHOPPING_KEYWORDS):
        return 'shopping'
    
    # Default to general chat
    return 'chat'

def call_openai(prompt, user_id):
    """Call OpenAI API for general conversation"""
    try:
        if not OPENAI_API_KEY:
            return "I'd love to chat, but I need an API key configured. You can still use my shopping features though!"
        
        # Get conversation history
        history = get_conversation_history(user_id)
        
        # Build messages
        messages = [
            {"role": "system", "content": "You are AI Pro, a friendly and helpful AI assistant. Keep responses concise and conversational, suitable for voice interaction. You can also help users shop on Amazon."}
        ]
        
        # Add history (last 5 messages)
        for msg in history[-5:]:
            messages.append({"role": msg['role'], "content": msg['content']})
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Call OpenAI
        data = json.dumps({
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 150,
            "temperature": 0.7
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'https://api.openai.com/v1/chat/completions',
            data=data,
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            answer = result['choices'][0]['message']['content']
            
            # Save to history
            save_conversation(user_id, prompt, answer)
            
            return answer
            
    except Exception as e:
        logger.error(f"OpenAI error: {str(e)}")
        return "I'm having trouble thinking right now. Let me help you shop instead - what are you looking for?"

def get_conversation_history(user_id):
    """Retrieve conversation history from DynamoDB"""
    try:
        response = users_table.get_item(Key={'userId': user_id})
        if 'Item' in response and 'conversation_history' in response['Item']:
            history_data = response['Item']['conversation_history']
            if isinstance(history_data, str):
                return json.loads(history_data)
            return history_data
        return []
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {str(e)}")
        return []

def save_conversation(user_id, user_message, assistant_message):
    """Save conversation to DynamoDB"""
    try:
        history = get_conversation_history(user_id)
        
        # Add new messages
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": assistant_message})
        
        # Keep only last 20 messages
        history = history[-20:]
        
        users_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='SET conversation_history = :history, last_updated = :timestamp',
            ExpressionAttributeValues={
                ':history': json.dumps(history),
                ':timestamp': datetime.now().isoformat()
            }
        )
        return True
    except Exception as e:
        logger.error(f"Error saving conversation: {str(e)}")
        return False

# Shopping cart functions (from previous implementation)
def get_user_cart(user_id):
    """Retrieve user's shopping cart from DynamoDB"""
    try:
        response = users_table.get_item(Key={'userId': user_id})
        if 'Item' in response and 'shopping_cart' in response['Item']:
            cart_data = response['Item']['shopping_cart']
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
        return True
    except Exception as e:
        logger.error(f"Error saving cart: {str(e)}")
        return False

def add_to_cart(user_id, product):
    """Add a product to user's cart"""
    cart = get_user_cart(user_id)
    
    for item in cart['items']:
        if item.get('url') == product.get('url'):
            return cart, False
    
    cart['items'].append(product)
    cart['total'] = sum(item.get('price', 0) for item in cart['items'])
    save_user_cart(user_id, cart)
    return cart, True

def clear_cart(user_id):
    """Clear all items from user's cart"""
    cart = {'items': [], 'total': 0.0}
    save_user_cart(user_id, cart)
    return cart

def get_apl_document_products(products, query):
    """Beautiful product listing APL (same as before)"""
    logger.info(f"Generating APL for query: {query}")
    logger.info(f"Products count: {len(products)}")
    if products:
        logger.info(f"First product: {products[0].get('name', 'N/A')}")
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
                                    "text": "Shopping Results",
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
                        {
                            "type": "Sequence",
                            "width": "100%",
                            "height": "70vh",
                            "scrollDirection": "vertical",
                            "data": "${payload.products}",
                            "numbered": False,
                            "background": "#ffffff",
                            "item": {
                                "type": "Container",
                                "width": "100%",
                                "paddingLeft": 20,
                                "paddingRight": 20,
                                "paddingTop": 16,
                                "paddingBottom": 16,
                                "items": [
                                    {
                                        "type": "Container",
                                        "width": "100%",
                                        "background": "#f7fafc",
                                        "borderRadius": 12,
                                        "borderWidth": 2,
                                        "borderColor": "#cbd5e0",
                                        "paddingLeft": 16,
                                        "paddingRight": 16,
                                        "paddingTop": 16,
                                        "paddingBottom": 16,
                                        "items": [
                                            {
                                                "type": "Container",
                                                "direction": "row",
                                                "items": [
                                                    {
                                                        "type": "Image",
                                                        "source": "${data.image_url}",
                                                        "width": 120,
                                                        "height": 120,
                                                        "scale": "best-fit",
                                                        "borderRadius": 8
                                                    },
                                                    {
                                                        "type": "Container",
                                                        "direction": "column",
                                                        "paddingLeft": 16,
                                                        "grow": 1,
                                                        "items": [
                                                            {
                                                                "type": "Text",
                                                                "text": "${data.name}",
                                                                "fontSize": 16,
                                                                "fontWeight": "bold",
                                                                "color": "#2d3748",
                                                                "maxLines": 2
                                                            },
                                                            {
                                                                "type": "Container",
                                                                "direction": "row",
                                                                "marginTop": 8,
                                                                "alignItems": "center",
                                                                "items": [
                                                                    {
                                                                        "type": "Text",
                                                                        "text": "$${data.price}",
                                                                        "fontSize": 20,
                                                                        "fontWeight": "bold",
                                                                        "color": "#48bb78"
                                                                    },
                                                                    {
                                                                        "type": "Text",
                                                                        "text": "⭐ ${data.rating}",
                                                                        "fontSize": 12,
                                                                        "color": "#f6ad55",
                                                                        "marginLeft": 12
                                                                    }
                                                                ]
                                                            },
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
                        }
                    ]
                }
            ]
        }
    }

def lambda_handler(event, context):
    """
    Enhanced Lambda handler with general AI chat + shopping
    Intelligently routes between conversation modes
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        user_id = event['session']['user']['userId']
        request_type = event['request']['type']
        session_attributes = event['session'].get('attributes', {})
        
        logger.info(f"User: {user_id}, Request Type: {request_type}")
        
        # Handle LaunchRequest
        if request_type == 'LaunchRequest':
            welcome_message = random.choice(WELCOME_MESSAGES)
            
            return {
                'version': '1.0',
                'sessionAttributes': session_attributes,
                'response': {
                    'outputSpeech': {
                        'type': 'PlainText',
                        'text': welcome_message
                    },
                    'shouldEndSession': False
                }
            }
        
        # Handle IntentRequest
        elif request_type == 'IntentRequest':
            intent_name = event['request']['intent']['name']
            logger.info(f"Intent: {intent_name}")
            
            # ========== GENERAL CHAT (LLMQueryIntent or general questions) ==========
            if intent_name == 'LLMQueryIntent' or intent_name == 'AMAZON.FallbackIntent':
                slots = event['request']['intent'].get('slots', {})
                query = slots.get('Query', {}).get('value', '')
                
                # If no query, use fallback
                if not query and intent_name == 'AMAZON.FallbackIntent':
                    query = "I didn't quite understand that. Can you rephrase?"
                
                logger.info(f"User query: {query}")
                
                # Detect intent: chat, shopping, or cart
                detected_intent = detect_intent(query)
                logger.info(f"Detected intent: {detected_intent}")
                
                # Route to appropriate handler
                if detected_intent == 'shopping':
                    # Extract product from query
                    product = query.lower()
                    for keyword in SHOPPING_KEYWORDS:
                        product = product.replace(keyword, '').strip()
                    
                    try:
                        tool_output = product_search_tool(product)
                        tool_data = json.loads(tool_output)
                        
                        if tool_data.get('status') == 'success':
                            products = tool_data.get('products', [])
                            
                            if products:
                                session_attributes['current_products'] = json.dumps(products)
                                
                                response_text = f"Great! I found {len(products)} awesome options for {product}. "
                                for i, p in enumerate(products[:3], 1):
                                    response_text += f"Item {i}: {p['name']} at ${p['price']:.2f}. "
                                response_text += "Say 'add item 1' to add any item to your cart!"
                                
                                logger.info(f"Sending APL with {len(products)} products to datasources")
                                
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
                                                'token': 'shopping-products-bright-v4-fixed',
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
                                response_text = f"I couldn't find any products for '{product}'. Try a different search term!"
                        else:
                            response_text = "I'm having trouble searching right now. Try again in a moment!"
                    except Exception as e:
                        logger.error(f"Shopping search error: {str(e)}")
                        response_text = "Oops, something went wrong with the search. Let's chat instead - what's on your mind?"
                
                elif detected_intent == 'cart':
                    cart = get_user_cart(user_id)
                    if cart['items']:
                        response_text = f"You have {len(cart['items'])} items in your cart totaling ${cart['total']:.2f}. Say 'checkout' when you're ready!"
                    else:
                        response_text = "Your cart is empty. Search for something to add!"
                
                else:  # General chat
                    response_text = call_openai(query, user_id)
            
            # ========== SHOPPING INTENT ==========
            elif intent_name == 'ShoppingIntent':
                slots = event['request']['intent'].get('slots', {})
                product = slots.get('Product', {}).get('value', '')
                price = slots.get('Price', {}).get('value', '')
                category = slots.get('Category', {}).get('value', '')
                
                logger.info(f"Shopping: {product}, Price: {price}, Category: {category}")
                
                try:
                    max_price = float(price) if price else None
                    tool_output = product_search_tool(product, max_price, category)
                    tool_data = json.loads(tool_output)
                    
                    if tool_data.get('status') == 'success':
                        products = tool_data.get('products', [])
                        
                        if products:
                            session_attributes['current_products'] = json.dumps(products)
                            
                            response_text = f"Perfect! I found {len(products)} great options for you. "
                            for i, p in enumerate(products[:3], 1):
                                response_text += f"Item {i}: {p['name']} at ${p['price']:.2f}. "
                            response_text += "Say 'add item 1' to add to your cart!"
                            
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
                                            'token': 'shopping-products-bright-v4-fixed',
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
                            response_text = f"I couldn't find '{product}'. Try a different search!"
                    else:
                        response_text = "Having trouble searching. Try again!"
                except Exception as e:
                    logger.error(f"Shopping error: {str(e)}")
                    response_text = "Oops! Error searching. Let's chat - what's up?"
            
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
                                response_text = f"Added {product['name']} to your cart! You now have {len(cart['items'])} items."
                            else:
                                response_text = "That's already in your cart!"
                        else:
                            response_text = f"I don't see item {item_number}. Can you try again?"
                    except Exception as e:
                        logger.error(f"Add to cart error: {str(e)}")
                        response_text = "Couldn't add that. Try again?"
                else:
                    response_text = "Let's search for products first! What are you looking for?"
            
            # ========== VIEW CART ==========
            elif intent_name == 'ViewCartIntent':
                cart = get_user_cart(user_id)
                
                if cart['items']:
                    response_text = f"You have {len(cart['items'])} items totaling ${cart['total']:.2f}. Say 'checkout' when ready!"
                else:
                    response_text = "Your cart is empty. Try searching for products!"
            
            # ========== HELP ==========
            elif intent_name == 'AMAZON.HelpIntent':
                response_text = "Just ask me anything! I can answer questions, find products, or help with your cart. What would you like?"
            
            # ========== STOP/CANCEL ==========
            elif intent_name in ['AMAZON.StopIntent', 'AMAZON.CancelIntent']:
                response_text = "Thanks for hanging out! Come back anytime you want to chat or shop. Bye!"
                
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
                response_text = "I'm not sure I understand. Can you rephrase that, or just ask me something?"
        
        else:
            response_text = "I didn't quite catch that. What did you say?"
        
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
                    'text': 'Sorry, something went wrong. Try again!'
                },
                'shouldEndSession': False
            }
        }

