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
                    
                    logger.info(f"Environment variables - OpenAI: {openai_api_key[:10] if openai_api_key else 'None'}..., Gemini: {gemini_api_key[:10] if gemini_api_key else 'None'}..., Claude: {claude_api_key[:10] if claude_api_key else 'None'}...")
                    
                    # Fallback to DynamoDB lookup if not in environment
                    if not openai_api_key or not gemini_api_key or not claude_api_key:
                        logger.info("Environment variables not found, falling back to DynamoDB lookup")
                        try:
                            dynamodb = boto3.resource('dynamodb')
                            table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'ai-assistant-users-dev'))
                            response = table.get_item(Key={'userId': user_id})
                            logger.info(f"DynamoDB response: {response}")
                            
                            if 'Item' in response:
                                user_data = response['Item']
                                logger.info(f"User data: {user_data}")
                                
                                # Handle DynamoDB string format (both raw strings and {"S": "value"} format)
                                if 'openai_api_key' in user_data:
                                    if isinstance(user_data['openai_api_key'], dict) and 'S' in user_data['openai_api_key']:
                                        openai_api_key = user_data['openai_api_key']['S']
                                    else:
                                        openai_api_key = str(user_data['openai_api_key'])
                                
                                if 'gemini_api_key' in user_data:
                                    if isinstance(user_data['gemini_api_key'], dict) and 'S' in user_data['gemini_api_key']:
                                        gemini_api_key = user_data['gemini_api_key']['S']
                                    else:
                                        gemini_api_key = str(user_data['gemini_api_key'])
                                
                                if 'claude_api_key' in user_data:
                                    if isinstance(user_data['claude_api_key'], dict) and 'S' in user_data['claude_api_key']:
                                        claude_api_key = user_data['claude_api_key']['S']
                                    else:
                                        claude_api_key = str(user_data['claude_api_key'])
                                
                                logger.info(f"Retrieved API keys - OpenAI: {openai_api_key[:10] if openai_api_key else 'None'}...")
                            else:
                                logger.warning(f"No user data found for user ID: {user_id}")
                        except Exception as e:
                            logger.error(f"Error retrieving API keys from DynamoDB: {str(e)}")
                    
                    # Final check for API keys
                    if not openai_api_key:
                        logger.error("OpenAI API key not found in environment variables or DynamoDB")
                        response_text = "Your OpenAI API key is not configured. Please set it up in the web portal."
                    else:
                        logger.info(f"OpenAI API key found: {openai_api_key[:10]}...")
                        
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
                                        'parts': [{'text': full_prompt}]
                                    }],
                                    'generationConfig': {
                                        'maxOutputTokens': 200,
                                        'temperature': 0.7
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
                                    'x-api-key': claude_api_key,
                                    'Content-Type': 'application/json',
                                    'anthropic-version': '2023-06-01'
                                }
                                
                                # Combine system prompt with user query
                                full_prompt = f"{voice_prompt}\n\nUser question: {query}"
                                
                                data = {
                                    'model': 'claude-3-haiku-20240307',
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
                
                except Exception as e:
                    logger.error(f"Error handling LLM query: {str(e)}")
                    response_text = f"I encountered an error: {str(e)}. But I received your query: '{query}'"
            
            elif intent_name == 'SetDefaultProviderIntent':
                # Handle setting default provider
                provider_slot = event['request']['intent']['slots']['Provider']
                provider = provider_slot.get('value', '').lower() if provider_slot else ''
                
                if provider in ['openai', 'claude', 'gemini']:
                    response_text = f"Okay, {provider} is now your default provider. You can now just ask your question."
                else:
                    response_text = "I didn't understand which provider you want to set as default. Please say 'Set OpenAI as my default' or 'Set Claude as my default' or 'Set Gemini as my default'."
            
            elif intent_name == 'ClearContextIntent':
                response_text = "Session context cleared. Starting a new conversation."
            
            elif intent_name == 'AMAZON.HelpIntent':
                response_text = "I'm AI Pro, your multi-provider AI assistant! You can ask me questions using different AI providers. Say 'Ask OpenAI, what is machine learning?' or set a default provider by saying 'Set Claude as my default'. What would you like to know?"
            
            elif intent_name in ['AMAZON.StopIntent', 'AMAZON.CancelIntent']:
                response_text = "Goodbye! Thanks for using AI Pro. I hope our conversation was helpful!"
            
            else:
                response_text = "I didn't understand that. You can ask me a question or say 'help' for instructions."
        
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
                    'text': 'Sorry, I encountered an error processing your request.'
                },
                'shouldEndSession': False
            }
        }
