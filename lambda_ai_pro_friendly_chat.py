# lambda_ai_pro_friendly_chat.py
# AI Pro - Friendly AI Research Assistant with Casual Chat & Subtle Shopping

import json
import boto3
import os
import logging
import urllib.request
import urllib.parse
import random
from datetime import datetime
from decimal import Decimal
from shopping_tools import product_search_tool

# Custom JSON encoder to handle Decimal objects from DynamoDB
class DecimalEncoder(json.JSONEncoder):
    """
    A custom JSON encoder that converts Decimal objects to float,
    preventing serialization errors when sending data to Alexa.
    """
    def default(self, o):
        if isinstance(o, Decimal):
            # Convert Decimal to float for JSON serialization
            return float(o)
        # Let the base class default method raise the TypeError
        return super(DecimalEncoder, self).default(o)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'ai-assistant-users-dev'))

# AI Provider Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')

# Friendly, casual welcome messages - research & chat focused
WELCOME_MESSAGES = [
    "Hey! I'm AI Pro. I love chatting about anything - science, history, tech, you name it! What's on your mind?",
    "Hi there! Ready to explore some interesting topics? Ask me anything!",
    "Hey! Whether you want to dive deep into a topic or just chat, I'm here. What would you like to talk about?",
    "Hello! I'm your friendly AI companion. Let's chat about something fascinating!",
    "Hi! From curious questions to deep research, I'm here to help. What interests you today?",
    "Hey there! I'm great at answering questions, researching topics, and just having a good conversation. What's up?"
]

# Shopping keywords (for subtle detection)
SHOPPING_KEYWORDS = [
    'buy', 'purchase', 'shop', 'shopping', 'find product', 'looking for',
    'need to buy', 'want to buy', 'where can i buy', 'show me', 'show',
    'find me', 'get me', 'i need', 'looking to purchase', 'for sale',
    'search for', 'find'
]

def detect_shopping_intent(text):
    """
    Detect if user specifically wants to shop (must be clear intent)
    """
    text_lower = text.lower()
    
    # Check for explicit shopping words
    has_shopping_word = any(keyword in text_lower for keyword in SHOPPING_KEYWORDS)
    
    # Check for product-like nouns (headphones, laptop, etc)
    product_indicators = ['headphones', 'laptop', 'phone', 'camera', 'vacuum', 
                         'blender', 'watch', 'shoes', 'backpack', 'speaker', 'headphone']
    has_product_context = any(prod in text_lower for prod in product_indicators)
    
    # Shopping if: explicit keywords OR (product + action words)
    action_words = ['show', 'find', 'best', 'recommend', 'need', 'want', 'get', 'search']
    has_action = any(word in text_lower for word in action_words)
    
    return has_shopping_word or (has_product_context and has_action)

def get_user_preferences(user_id):
    """Get user's preferred AI provider"""
    try:
        response = users_table.get_item(Key={'userId': user_id})
        if 'Item' in response:
            return response['Item'].get('preferred_ai_provider', 'openai')
        return 'openai'
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        return 'openai'

def set_user_preference(user_id, provider):
    """Set user's preferred AI provider"""
    try:
        users_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='SET preferred_ai_provider = :provider',
            ExpressionAttributeValues={':provider': provider}
        )
        return True
    except Exception as e:
        logger.error(f"Error setting preference: {str(e)}")
        return False

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
        
        # Keep only last 20 messages for context
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

def call_openai(prompt, user_id):
    """Call OpenAI GPT for friendly conversation"""
    try:
        if not OPENAI_API_KEY:
            return "I'd love to chat using OpenAI, but I need an API key configured. Try asking me to use Gemini or Claude instead!"
        
        history = get_conversation_history(user_id)
        
        messages = [
            {"role": "system", "content": "You are AI Pro, a friendly, knowledgeable, and enthusiastic AI assistant. You love discussing any topic - science, history, technology, philosophy, current events, trivia, and more. Keep responses conversational, engaging, and suitable for voice interaction. Be curious, helpful, and fun to talk to."}
        ]
        
        # Add recent conversation history
        for msg in history[-5:]:
            messages.append({"role": msg['role'], "content": msg['content']})
        
        messages.append({"role": "user", "content": prompt})
        
        data = json.dumps({
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 200,
            "temperature": 0.8
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
            save_conversation(user_id, prompt, answer)
            return answer
            
    except Exception as e:
        logger.error(f"OpenAI error: {str(e)}")
        return "Hmm, I'm having trouble with OpenAI right now. Want to try asking me to use Gemini or Claude?"

def call_anthropic(prompt, user_id):
    """Call Anthropic Claude for conversation"""
    try:
        if not ANTHROPIC_API_KEY:
            return "I'd love to chat using Claude, but I need an API key configured. Try OpenAI or Gemini instead!"
        
        history = get_conversation_history(user_id)
        
        # Build context from history
        context = ""
        for msg in history[-5:]:
            role = "Human" if msg['role'] == 'user' else "Assistant"
            context += f"\n{role}: {msg['content']}"
        
        full_prompt = f"{context}\n\nHuman: {prompt}\n\nAssistant:"
        
        data = json.dumps({
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 200,
            "temperature": 0.8,
            "system": "You are AI Pro, a friendly, knowledgeable AI assistant who loves discussing any topic with enthusiasm. Keep responses conversational and voice-friendly.",
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=data,
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            answer = result['content'][0]['text']
            save_conversation(user_id, prompt, answer)
            return answer
            
    except Exception as e:
        logger.error(f"Anthropic error: {str(e)}")
        return "Claude is having a moment. Want to try with OpenAI or Gemini?"

def call_gemini(prompt, user_id):
    """Call Google Gemini for conversation"""
    try:
        if not GOOGLE_API_KEY:
            return "I'd love to chat using Gemini, but I need an API key configured. Try OpenAI or Claude!"
        
        history = get_conversation_history(user_id)
        
        # Build context
        context = ""
        for msg in history[-5:]:
            role = "user" if msg['role'] == 'user' else 'model'
            context += f"\n{role}: {msg['content']}"
        
        full_prompt = f"{context}\n\nuser: {prompt}"
        
        data = json.dumps({
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 200,
                "topP": 0.95
            },
            "systemInstruction": {
                "parts": [{
                    "text": "You are AI Pro, a friendly, knowledgeable AI assistant who loves discussing any topic with enthusiasm. Keep responses conversational and voice-friendly."
                }]
            }
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}',
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            answer = result['candidates'][0]['content']['parts'][0]['text']
            save_conversation(user_id, prompt, answer)
            return answer
            
    except Exception as e:
        logger.error(f"Gemini error: {str(e)}")
        return "Gemini is taking a break. Try asking me to use OpenAI or Claude!"

def handle_ai_chat(prompt, user_id, provider=None):
    """Route to appropriate AI provider"""
    
    # Detect provider from query
    prompt_lower = prompt.lower()
    if not provider:
        if 'gemini' in prompt_lower or 'google' in prompt_lower:
            provider = 'gemini'
            prompt = prompt.replace('gemini', '').replace('Gemini', '').replace('google', '').replace('Google', '').strip()
        elif 'claude' in prompt_lower or 'anthropic' in prompt_lower:
            provider = 'anthropic'
            prompt = prompt.replace('claude', '').replace('Claude', '').replace('anthropic', '').replace('Anthropic', '').strip()
        elif 'openai' in prompt_lower or 'gpt' in prompt_lower:
            provider = 'openai'
            prompt = prompt.replace('openai', '').replace('OpenAI', '').replace('gpt', '').replace('GPT', '').strip()
        else:
            # Use user's preference or default
            provider = get_user_preferences(user_id)
    
    logger.info(f"Using AI provider: {provider}")
    
    # Call appropriate provider
    if provider == 'gemini':
        return call_gemini(prompt, user_id)
    elif provider == 'anthropic':
        return call_anthropic(prompt, user_id)
    else:
        return call_openai(prompt, user_id)

# Shopping functions (unchanged from before)
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
    """ABSOLUTE MINIMAL APL - Plain text only, no emojis, white background"""
    logger.info(f"GENERATING ABSOLUTE MINIMAL APL for {len(products)} products")
    
    # Build simple product list - BRIGHT COLORS + THIN FONT
    product_list = []
    product_list.append({
        "type": "Text",
        "text": f"Shopping Results: {query.title()}",
        "fontSize": 36,
        "fontFamily": "amazon-ember-display",
        "fontWeight": "100",
        "color": "#ffffff",
        "textAlign": "center",
        "paddingBottom": 15
    })
    
    product_list.append({
        "type": "Text",
        "text": f"{len(products)} products found - Scroll for more",
        "fontSize": 18,
        "fontFamily": "amazon-ember-display",
        "fontWeight": "300",
        "color": "#aaaaaa",
        "textAlign": "center",
        "paddingBottom": 25
    })
    
    # Add each product with IMAGE - ALL 10 PRODUCTS!
    for i, product in enumerate(products[:10], 1):
        product_list.append({
            "type": "Container",
            "direction": "row",
            "width": "95%",
            "backgroundColor": "#2a2a2a",
            "borderRadius": 12,
            "borderWidth": 2,
            "borderColor": "#4a90e2",
            "padding": 20,
            "marginBottom": 20,
            "items": [
                {
                    "type": "Image",
                    "source": product.get('image_url', ''),
                    "width": 120,
                    "height": 120,
                    "scale": "best-fill",
                    "borderRadius": 8,
                    "backgroundColor": "#1a1a1a"
                },
                {
                    "type": "Container",
                    "paddingLeft": 20,
                    "grow": 1,
                    "items": [
                        {
                            "type": "Text",
                            "text": f"#{i}",
                            "fontSize": 14,
                            "fontFamily": "amazon-ember-display",
                            "fontWeight": "300",
                            "color": "#4a90e2",
                            "paddingBottom": 5
                        },
                        {
                            "type": "Text",
                            "text": product['name'][:65],
                            "fontSize": 18,
                            "fontFamily": "amazon-ember-display",
                            "fontWeight": "300",
                            "color": "#ffffff",
                            "maxLines": 2
                        },
                        {
                            "type": "Text",
                            "text": f"${product['price']:.2f}",
                            "fontSize": 28,
                            "fontFamily": "amazon-ember-display",
                            "fontWeight": "300",
                            "color": "#00ff00",
                            "paddingTop": 8
                        },
                        {
                            "type": "Text",
                            "text": f"{product['rating']}/5 stars",
                            "fontSize": 14,
                            "fontFamily": "amazon-ember-display",
                            "fontWeight": "300",
                            "color": "#ffaa00",
                            "paddingTop": 5
                        }
                    ]
                }
            ]
        })
    
    return {
        "type": "APL",
        "version": "2023.3",
        "mainTemplate": {
            "parameters": [],
            "items": [{
                "type": "Container",
                "width": "100vw",
                "height": "100vh",
                "backgroundColor": "#000000",
                "paddingLeft": 30,
                "paddingRight": 30,
                "paddingTop": 30,
                "items": product_list
            }]
        }
    }

def get_apl_document_products_COMPLEX_BACKUP(products, query):
    """Return SIMPLE BRIGHT APL that WORKS - No fancy gradients"""
    # Simple bright design - pure white background, works 100%
    logger.info(f"GENERATING APL with background: white, {len(products)} products")
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
                    "background": "white",
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
                            "height": "75vh",
                            "paddingLeft": 40,
                            "paddingRight": 40,
                            "scrollDirection": "vertical",
                            "data": "${payload.products}",
                            "numbered": True,
                            "item": {
                                "type": "Container",
                                "width": "100%",
                                "background": "#f7fafc",
                                "borderRadius": 15,
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
                                                "width": 150,
                                                "height": 150,
                                                "scale": "best-fit",
                                                "borderRadius": 15
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
                                                                "color": "#2d3748",
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
                                                                        "color": "#48bb78"
                                                                    },
                                                                    {
                                                                        "type": "Container",
                                                                        "paddingLeft": 20,
                                                                        "items": [
                                                                            {
                                                                                "type": "Text",
                                                                                "text": "⭐ ${data.rating}/5",
                                                                                "fontSize": 14,
                                                                                "color": "#f6ad55"
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "type": "Text",
                                                                "text": "${data.description}",
                                                                "fontSize": 14,
                                                                "color": "#718096",
                                                                "maxLines": 2,
                                                                "marginTop": 10
                                                            },
                                                            {
                                                                "type": "Container",
                                                                "marginTop": 15,
                                                                "padding": 15,
                                                                "background": {
                                                                    "type": "LinearGradient",
                                                                    "colorRange": ["#667eea", "#764ba2"],
                                                                    "inputRange": [0, 1],
                                                                    "angle": 135
                                                                },
                                                                "borderRadius": 12,
                                                                "items": [
                                                                    {
                                                                        "type": "Text",
                                                                        "text": "🛒 Say: Add item ${index+1}",
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
                    ]
                }
            ]
        }
    }

def lambda_handler(event, context):
    """
    Enhanced Lambda handler - Friendly AI Research Assistant
    Primary: General conversation, research, curiosity
    Secondary: Shopping when explicitly requested
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        user_id = event['session']['user']['userId']
        request_type = event['request']['type']
        session_attributes = event['session'].get('attributes', {})
        
        logger.info(f"User: {user_id}, Request Type: {request_type}")
        
        # ========== LAUNCH REQUEST ==========
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
        
        # ========== INTENT REQUEST ==========
        elif request_type == 'IntentRequest':
            intent_name = event['request']['intent']['name']
            logger.info(f"Intent: {intent_name}")
            
            # ========== GENERAL CHAT & RESEARCH (Primary Feature) ==========
            if intent_name == 'LLMQueryIntent' or intent_name == 'AMAZON.FallbackIntent':
                slots = event['request']['intent'].get('slots', {})
                query = slots.get('Query', {}).get('value', '')
                
                if not query and intent_name == 'AMAZON.FallbackIntent':
                    query = "I didn't quite catch that. Can you say that again?"
                
                logger.info(f"User query: {query}")
                
                # Check if this is a shopping request (must be explicit)
                if detect_shopping_intent(query):
                    logger.info("Shopping intent detected")
                    
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
                                logger.info(f"LLMQueryIntent: Found {len(products)} products for shopping query")
                                
                                # Clean products data - ensure JSON serializable
                                products_clean = json.loads(json.dumps(products, cls=DecimalEncoder))
                                logger.info(f"Products cleaned and serialized successfully")
                                
                                session_attributes['current_products'] = json.dumps(products_clean)
                                
                                response_text = f"Sure! I found {len(products)} great options for {product}. "
                                for i, p in enumerate(products[:3], 1):
                                    response_text += f"Option {i}: {p['name']} at ${p['price']:.2f}. "
                                response_text += "Say 'add item 1' if you'd like to add any!"
                                
                                logger.info(f"Building APL for LLMQueryIntent shopping path...")
                                apl_doc = get_apl_document_products(products_clean, product)
                                logger.info(f"APL document created for LLMQueryIntent")
                                
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
                                                'token': 'shopping-products-bright',
                                                'document': apl_doc,
                                                'datasources': {
                                                    'payload': {
                                                        'products': products_clean,
                                                        'query': product
                                                    }
                                                }
                                            }
                                        ],
                                        'shouldEndSession': False
                                    }
                                }
                            else:
                                response_text = f"Hmm, I couldn't find products for '{product}'. Want to chat about something else?"
                        else:
                            response_text = "Shopping search isn't working right now. But I'm great at answering questions! What would you like to know?"
                    except Exception as e:
                        logger.error(f"Shopping error: {str(e)}")
                        response_text = "Shopping isn't available right now, but I'd love to chat! What's on your mind?"
                
                else:
                    # DEFAULT: General AI chat/research
                    logger.info("General chat intent")
                    response_text = handle_ai_chat(query, user_id)
            
            # ========== SET AI PROVIDER PREFERENCE ==========
            elif intent_name == 'SetDefaultProviderIntent':
                slots = event['request']['intent'].get('slots', {})
                provider = slots.get('Provider', {}).get('value', '').lower()
                
                if provider in ['openai', 'claude', 'anthropic', 'gemini', 'google']:
                    if provider == 'google':
                        provider = 'gemini'
                    if provider == 'anthropic':
                        provider = 'anthropic'
                    
                    set_user_preference(user_id, provider)
                    response_text = f"Got it! I'll use {provider.title()} by default now. Just ask me anything!"
                else:
                    response_text = "I support OpenAI, Claude, and Gemini. Which would you like as your default?"
            
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
                                response_text = f"Added {product['name']} to your cart! Anything else you'd like to know or shop for?"
                            else:
                                response_text = "That's already in your cart! What else can I help with?"
                        else:
                            response_text = f"I don't see item {item_number}. Try again or ask me something else!"
                    except Exception as e:
                        logger.error(f"Add to cart error: {str(e)}")
                        response_text = "Couldn't add that. Want to chat about something instead?"
                else:
                    response_text = "Let's find products first! What are you looking for?"
            
            # ========== VIEW CART ==========
            elif intent_name == 'ViewCartIntent':
                cart = get_user_cart(user_id)
                
                if cart['items']:
                    response_text = f"You have {len(cart['items'])} items totaling ${cart['total']:.2f}. Anything else I can help with?"
                else:
                    response_text = "Your cart is empty. Want to chat or search for products?"
            
            # ========== SHOPPING INTENT (Direct Product Search) ==========
            elif intent_name == 'ShoppingIntent':
                logger.info(">>> EXECUTING SHOPPING INTENT HANDLER - CODE PATH CONFIRMED <<<")
                
                slots = event['request']['intent'].get('slots', {})
                product = slots.get('Product', {}).get('value', '')
                price = slots.get('Price', {}).get('value', '')
                category = slots.get('Category', {}).get('value', '')
                
                logger.info(f"Shopping: Product={product}, Price={price}, Category={category}")
                
                try:
                    logger.info(f"Starting product search for: {product}")
                    max_price = float(price) if price else None
                    tool_output = product_search_tool(product, max_price, category)
                    logger.info(f"Product search completed, parsing results...")
                    tool_data = json.loads(tool_output)
                    logger.info(f"Tool response status: {tool_data.get('status')}")
                    
                    if tool_data.get('status') == 'success':
                        products = tool_data.get('products', [])
                        
                        if products:
                            logger.info(f"Found {len(products)} products, generating APL...")
                            
                            # Clean products data - ensure JSON serializable
                            products_clean = json.loads(json.dumps(products, cls=DecimalEncoder))
                            logger.info(f"Products cleaned and serialized successfully")
                            
                            session_attributes['current_products'] = json.dumps(products_clean)
                            
                            response_text = f"Perfect! I found {len(products)} great options for {product}. "
                            for i, p in enumerate(products[:3], 1):
                                response_text += f"Option {i}: {p['name']} at ${p['price']:.2f}. "
                            response_text += "Say 'add item 1' to add to your cart!"
                            
                            logger.info(f"Building APL document for {len(products_clean)} products...")
                            apl_doc = get_apl_document_products(products_clean, product)
                            logger.info(f"APL document created, sending response...")
                            
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
                                            'token': 'shopping-products-bright',
                                            'document': apl_doc,
                                            'datasources': {
                                                'payload': {
                                                    'products': products_clean,
                                                    'query': product
                                                }
                                            }
                                        }
                                    ],
                                    'shouldEndSession': False
                                }
                            }
                        else:
                            response_text = f"I couldn't find products for '{product}'. Try a different search or ask me something else!"
                    else:
                        response_text = "Shopping search isn't working right now. But I'd love to chat! What's on your mind?"
                except Exception as e:
                    logger.error(f"Shopping error: {str(e)}")
                    response_text = "Oops! Shopping isn't available right now. Want to chat instead?"
            
            # ========== HELP ==========
            elif intent_name == 'AMAZON.HelpIntent':
                response_text = "I'm AI Pro, your friendly AI assistant! Ask me anything - history, science, tech, trivia, research, or even help finding products. What interests you?"
            
            # ========== STOP/CANCEL ==========
            elif intent_name in ['AMAZON.StopIntent', 'AMAZON.CancelIntent']:
                response_text = "Great chatting with you! Come back anytime you want to explore something interesting. Bye!"
                
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
                response_text = "Not sure I got that. Want to chat about something or ask me a question?"
        
        else:
            response_text = "Didn't quite catch that. What's on your mind?"
        
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
                    'text': 'Oops, something went wrong. Try asking me again!'
                },
                'shouldEndSession': False
            }
        }

