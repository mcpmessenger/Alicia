import json
import boto3
import os
import logging
import urllib.request
import urllib.parse

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_apl_document():
    """Return the APL document for display devices"""
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
                            "height": "auto",
                            "paddingTop": 40,
                            "paddingBottom": 20,
                            "paddingLeft": 40,
                            "paddingRight": 40,
                            "items": [
                                {
                                    "type": "Container",
                                    "direction": "row",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "items": [
                                        {
                                            "type": "Container",
                                            "width": 60,
                                            "height": 60,
                                            "borderRadius": 30,
                                            "background": {
                                                "type": "LinearGradient",
                                                "colorRange": ["#00d4ff", "#0099cc", "#0066ff"],
                                                "inputRange": [0, 0.5, 1],
                                                "angle": 45
                                            },
                                            "boxShadow": "0 0 20px rgba(0, 212, 255, 0.3)",
                                            "items": [
                                                {
                                                    "type": "Text",
                                                    "text": "🤖",
                                                    "fontSize": 24,
                                                    "color": "white",
                                                    "textAlign": "center",
                                                    "textAlignVertical": "center"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "Container",
                                            "paddingLeft": 20,
                                            "items": [
                                                {
                                                    "type": "Text",
                                                    "text": "AI Pro",
                                                    "fontSize": 32,
                                                    "fontWeight": "bold",
                                                    "color": {
                                                        "type": "LinearGradient",
                                                        "colorRange": ["#00d4ff", "#0099cc", "#0066ff"],
                                                        "inputRange": [0, 0.5, 1],
                                                        "angle": 45
                                                    }
                                                },
                                                {
                                                    "type": "Text",
                                                    "text": "Multi-Provider AI Assistant",
                                                    "fontSize": 14,
                                                    "color": "#a0a0a0",
                                                    "marginTop": 5
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "Container",
                            "width": "100%",
                            "height": "auto",
                            "paddingLeft": 40,
                            "paddingRight": 40,
                            "paddingBottom": 20,
                            "items": [
                                {
                                    "type": "Container",
                                    "width": "100%",
                                    "background": "rgba(255, 255, 255, 0.05)",
                                    "borderRadius": 20,
                                    "borderWidth": 1,
                                    "borderColor": "rgba(255, 255, 255, 0.1)",
                                    "padding": 30,
                                    "boxShadow": "0 8px 32px rgba(0, 0, 0, 0.3)",
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "${payload.responseText}",
                                            "fontSize": 18,
                                            "color": "#ffffff",
                                            "textAlign": "left",
                                            "lineHeight": 1.6,
                                            "width": "100%"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "Container",
                            "width": "100%",
                            "height": "auto",
                            "paddingLeft": 40,
                            "paddingRight": 40,
                            "paddingBottom": 40,
                            "items": [
                                {
                                    "type": "Container",
                                    "direction": "row",
                                    "justifyContent": "spaceBetween",
                                    "alignItems": "center",
                                    "items": [
                                        {
                                            "type": "Container",
                                            "direction": "row",
                                            "alignItems": "center",
                                            "items": [
                                                {
                                                    "type": "Container",
                                                    "width": 8,
                                                    "height": 8,
                                                    "borderRadius": 4,
                                                    "background": "#00ff00",
                                                    "boxShadow": "0 0 10px rgba(0, 255, 0, 0.5)",
                                                    "marginRight": 8
                                                },
                                                {
                                                    "type": "Text",
                                                    "text": "System Online",
                                                    "fontSize": 12,
                                                    "color": "#00ff00",
                                                    "fontWeight": "500"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "Text",
                                            "text": "© 2025 AI Pro",
                                            "fontSize": 12,
                                            "color": "#a0a0a0"
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
    """Secure version - uses environment variables and DynamoDB for API keys"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract user ID and request type
        user_id = event['session']['user']['userId']
        request_type = event['request']['type']
        
        logger.info(f"User ID: {user_id}, Request Type: {request_type}")
        
        # Handle different request types
        if request_type == 'LaunchRequest':
            response_text = "Welcome to AI Pro! I'm your voice-optimized AI assistant with OpenAI, Gemini, and Claude. Ask me anything and I'll give you concise, spoken responses. Try saying 'Ask OpenAI, what is machine learning?' or 'Ask Gemini, tell me about space' or 'Ask Claude, explain quantum computing'."
            
        elif request_type == 'IntentRequest':
            intent_name = event['request']['intent']['name']
            logger.info(f"Intent: {intent_name}")
            
            if intent_name == 'LLMQueryIntent':
                # Handle LLM query
                query_slot = event['request']['intent']['slots']['Query']
                query = query_slot.get('value', '') if query_slot else ''
                logger.info(f"Query: {query}")
                
                try:
                    # Get API keys from environment variables or DynamoDB
                    openai_api_key = os.environ.get('OPENAI_API_KEY')
                    gemini_api_key = os.environ.get('GEMINI_API_KEY')
                    claude_api_key = os.environ.get('CLAUDE_API_KEY')
                    
                    # Fallback to DynamoDB lookup if not in environment
                    if not openai_api_key or not gemini_api_key or not claude_api_key:
                        try:
                            dynamodb = boto3.resource('dynamodb')
                            table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'ai-assistant-users-dev'))
                            response = table.get_item(Key={'userId': user_id})
                            if 'Item' in response:
                                user_data = response['Item']
                                openai_api_key = user_data.get('openai_api_key', openai_api_key)
                                gemini_api_key = user_data.get('gemini_api_key', gemini_api_key)
                                claude_api_key = user_data.get('claude_api_key', claude_api_key)
                        except Exception as e:
                            logger.error(f"Error retrieving API keys from DynamoDB: {str(e)}")
                    
                    # Check if user wants a specific provider
                    provider = None
                    if 'ask openai' in query.lower():
                        provider = 'openai'
                    elif 'ask claude' in query.lower():
                        provider = 'claude'
                    elif 'ask gemini' in query.lower():
                        provider = 'gemini'
                    
                    # Use OpenAI as default for testing
                    if not provider:
                        provider = 'openai'
                    
                    logger.info(f"Using provider: {provider}")
                    
                    # Simple voice prompt
                    voice_prompt = "You are responding through Alexa voice interface. Keep responses to 2-3 sentences maximum. Use natural, conversational speech. End with a brief follow-up question when appropriate. Speak as if talking to a friend."
                    
                    # Route to appropriate provider
                    if provider == 'openai':
                        if not openai_api_key:
                            response_text = "Your OpenAI API key is not configured. Please set it up in the web portal."
                        else:
                            logger.info("Attempting OpenAI API call")
                            # OpenAI API request
                            url = 'https://api.openai.com/v1/chat/completions'
                            headers = {
                                'Authorization': f'Bearer {openai_api_key}',
                                'Content-Type': 'application/json'
                            }
                            
                            data = {
                                'model': 'gpt-3.5-turbo',
                                'messages': [
                                    {'role': 'system', 'content': voice_prompt},
                                    {'role': 'user', 'content': query}
                                ],
                                'max_tokens': 200,
                                'temperature': 0.7
                            }
                            
                            # Make the API call
                            req = urllib.request.Request(
                                url, 
                                data=json.dumps(data).encode('utf-8'),
                                headers=headers,
                                method='POST'
                            )
                            
                            with urllib.request.urlopen(req, timeout=10) as response:
                                response_data = json.loads(response.read().decode('utf-8'))
                                if 'choices' in response_data and len(response_data['choices']) > 0:
                                    response_text = response_data['choices'][0]['message']['content']
                                    logger.info(f"OpenAI response received: {response_text[:100]}...")
                                else:
                                    response_text = "I'm sorry, I couldn't generate a response. Please try again."
                    
                    elif provider == 'gemini':
                        if not gemini_api_key:
                            response_text = "Your Gemini API key is not configured. Please set it up in the web portal."
                        else:
                            logger.info("Attempting Gemini API call")
                            # Gemini API request
                            url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={gemini_api_key}'
                            headers = {
                                'Content-Type': 'application/json'
                            }
                            
                            # Combine system prompt with user query
                            full_prompt = f"{voice_prompt}\n\nUser question: {query}"
                            
                            data = {
                                'contents': [{
                                    'parts': [{
                                        'text': full_prompt
                                    }]
                                }],
                                'generationConfig': {
                                    'temperature': 0.7,
                                    'maxOutputTokens': 200,
                                    'topP': 0.8,
                                    'topK': 40
                                }
                            }
                            
                            # Make the API call
                            req = urllib.request.Request(
                                url, 
                                data=json.dumps(data).encode('utf-8'),
                                headers=headers,
                                method='POST'
                            )
                            
                            with urllib.request.urlopen(req, timeout=10) as response:
                                response_data = json.loads(response.read().decode('utf-8'))
                                if 'candidates' in response_data and len(response_data['candidates']) > 0:
                                    response_text = response_data['candidates'][0]['content']['parts'][0]['text']
                                    logger.info(f"Gemini response received: {response_text[:100]}...")
                                else:
                                    response_text = "I'm sorry, I couldn't generate a response. Please try again."
                    
                    elif provider == 'claude':
                        if not claude_api_key:
                            response_text = "Your Claude API key is not configured. Please set it up in the web portal."
                        else:
                            logger.info("Attempting Claude API call")
                            # Claude API request
                            url = 'https://api.anthropic.com/v1/messages'
                            headers = {
                                'Content-Type': 'application/json',
                                'x-api-key': claude_api_key,
                                'anthropic-version': '2023-06-01'
                            }
                            
                            # Combine system prompt with user query
                            full_prompt = f"{voice_prompt}\n\nUser question: {query}"
                            
                            data = {
                                'model': 'claude-3-5-sonnet-20241022',
                                'max_tokens': 200,
                                'messages': [{
                                    'role': 'user',
                                    'content': full_prompt
                                }]
                            }
                            
                            # Make the API call
                            req = urllib.request.Request(
                                url, 
                                data=json.dumps(data).encode('utf-8'),
                                headers=headers,
                                method='POST'
                            )
                            
                            with urllib.request.urlopen(req, timeout=10) as response:
                                response_data = json.loads(response.read().decode('utf-8'))
                                if 'content' in response_data and len(response_data['content']) > 0:
                                    response_text = response_data['content'][0]['text']
                                    logger.info(f"Claude response received: {response_text[:100]}...")
                                else:
                                    response_text = "I'm sorry, I couldn't generate a response. Please try again."
                    
                    else:
                        response_text = f"Provider {provider} is not yet supported. Please use OpenAI, Gemini, or Claude."
                            
                except urllib.error.HTTPError as e:
                    logger.error(f"{provider.title()} API HTTP Error: {e.code} - {e.reason}")
                    response_text = f"I encountered an error with {provider.title()}: HTTP Error {e.code}: {e.reason}. But I received your query: '{query}'. What would you like to know about {query}?"
                except urllib.error.URLError as e:
                    logger.error(f"{provider.title()} API URL Error: {str(e)}")
                    response_text = f"I encountered a connection error with {provider.title()}: {str(e)}. But I received your query: '{query}'. What would you like to know about {query}?"
                except Exception as e:
                    logger.error(f"{provider.title()} API error: {str(e)}")
                    response_text = f"I encountered an error with {provider.title()}: {str(e)}. But I received your query: '{query}'. What would you like to know about {query}?"
                    
            elif intent_name == 'SetDefaultProviderIntent':
                response_text = "You can set your default provider in the web portal. OpenAI, Gemini, and Claude are all supported for voice-optimized responses."
                
            elif intent_name == 'ClearContextIntent':
                response_text = "Context cleared. Starting a new conversation. Ask me anything!"
                
            elif intent_name == 'AMAZON.HelpIntent':
                response_text = "I'm your voice-optimized AI assistant with OpenAI, Gemini, and Claude! I give concise, spoken responses perfect for Alexa. Try saying 'Ask OpenAI, what is machine learning?' or 'Ask Gemini, tell me about space' or 'Ask Claude, explain quantum computing'. I'll keep my answers short and end with follow-up questions to keep our conversation flowing."
                
            else:
                response_text = "I didn't understand that. You can ask me a question or say 'help' for instructions."
                
        elif request_type == 'SessionEndedRequest':
            response_text = "Goodbye! Thanks for using AI Pro. I hope our conversation was helpful!"
            
        else:
            response_text = "I didn't understand that. You can ask me a question or say 'help' for instructions."
        
        # Check if device supports display
        supports_display = False
        if 'context' in event and 'System' in event['context']:
            system = event['context']['System']
            if 'device' in system and 'supportedInterfaces' in system['device']:
                supported_interfaces = system['device']['supportedInterfaces']
                supports_display = 'Alexa.Presentation.APL' in supported_interfaces
        
        response = {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': response_text
                },
                'shouldEndSession': False
            }
        }
        
        # Add APL directive if device supports display
        if supports_display:
            response['response']['directives'] = [
                {
                    'type': 'Alexa.Presentation.APL.RenderDocument',
                    'token': 'ai-pro-document',
                    'document': get_apl_document(),
                    'datasources': {
                        'payload': {
                            'responseText': response_text
                        }
                    }
                }
            ]
        
        return response
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': f'Sorry, I encountered an error processing your request. Details: {str(e)}'
                },
                'shouldEndSession': True
            }
        }
