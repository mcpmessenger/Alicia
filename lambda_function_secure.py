import json
import boto3
import os
import logging
import urllib.request
import urllib.parse

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Secure Lambda handler for Alexa Skill - GitHub version without hardcoded keys"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract user ID and request type
        user_id = event['session']['user']['userId']
        request_type = event['request']['type']
        
        logger.info(f"User ID: {user_id}, Request Type: {request_type}")
        
        # Handle different request types
        if request_type == 'LaunchRequest':
            response_text = "Welcome to AI Assistant Pro! You can ask me questions using different AI providers. Say 'Ask OpenAI, what is machine learning?' or set a default provider by saying 'Set Claude as my default'. To get started, you'll need to configure your API keys in the Alexa app."
            
        elif request_type == 'IntentRequest':
            intent_name = event['request']['intent']['name']
            logger.info(f"Intent: {intent_name}")
            
            if intent_name == 'LLMQueryIntent':
                # Handle LLM query with secure API key retrieval
                query_slot = event['request']['intent']['slots']['Query']
                query = query_slot.get('value', '') if query_slot else ''
                logger.info(f"Query: {query}")
                
                try:
                    # Get API key from environment variable or DynamoDB
                    api_key = os.environ.get('OPENAI_API_KEY')
                    if not api_key:
                        # Fallback to DynamoDB lookup
                        dynamodb = boto3.resource('dynamodb')
                        table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'ai-assistant-users-dev'))
                        response = table.get_item(Key={'userId': user_id})
                        if 'Item' in response:
                            api_key = response['Item'].get('openai_api_key')
                    
                    if not api_key:
                        response_text = "Your OpenAI API key is not configured. Please set it up in the web portal."
                    else:
                        # Prepare the request
                        url = 'https://api.openai.com/v1/chat/completions'
                        headers = {
                            'Authorization': f'Bearer {api_key}',
                            'Content-Type': 'application/json'
                        }
                        
                        data = {
                            'model': 'gpt-3.5-turbo',
                            'messages': [
                                {'role': 'user', 'content': query}
                            ],
                            'max_tokens': 500,
                            'temperature': 0.7
                        }
                        
                        # Make the API call
                        req = urllib.request.Request(
                            url, 
                            data=json.dumps(data).encode('utf-8'),
                            headers=headers,
                            method='POST'
                        )
                        
                        with urllib.request.urlopen(req) as response:
                            response_data = json.loads(response.read().decode('utf-8'))
                            response_text = response_data['choices'][0]['message']['content']
                            
                except urllib.error.HTTPError as e:
                    logger.error(f"OpenAI API HTTP Error: {e.code} - {e.reason}")
                    if e.code == 401:
                        response_text = "Your OpenAI API key is invalid. Please check your configuration."
                    else:
                        response_text = f"I encountered an error with OpenAI: HTTP Error {e.code}: {e.reason}"
                except Exception as e:
                    logger.error(f"OpenAI API error: {str(e)}")
                    response_text = f"I encountered an error with OpenAI: {str(e)}"
                    
            elif intent_name == 'SetDefaultProviderIntent':
                response_text = "Setting default provider is not supported in this simplified version."
                
            elif intent_name == 'ClearContextIntent':
                response_text = "Context cleared. Starting a new conversation."
                
            elif intent_name == 'AMAZON.HelpIntent':
                response_text = "AI Assistant Pro allows you to interact with OpenAI. You can say 'Ask OpenAI, what is the capital of France?'"
                
            else:
                response_text = "I didn't understand that. You can ask me a question or say 'help' for instructions."
                
        elif request_type == 'SessionEndedRequest':
            response_text = "Goodbye! Thanks for using AI Assistant Pro."
            
        else:
            response_text = "I didn't understand that. You can ask me a question or say 'help' for instructions."
        
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
