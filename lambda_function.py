import json
import boto3
import os
import logging
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
import openai
import anthropic
import google.generativeai as genai

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
kms = boto3.client('kms')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
kms_key_id = os.environ['KMS_KEY_ID']

class LLMProvider:
    """Abstract base class for LLM providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        openai.api_key = api_key
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": f"{context}\n{prompt}"}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"Sorry, I encountered an error with OpenAI: {str(e)}"

class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": f"{context}\n{prompt}"
                }]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return f"Sorry, I encountered an error with Claude: {str(e)}"

class GoogleProvider(LLMProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        try:
            response = self.model.generate_content(
                f"{context}\n{prompt}",
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.7
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Google API error: {str(e)}")
            return f"Sorry, I encountered an error with Gemini: {str(e)}"

class AIAssistantSkill:
    """Main Alexa Skill handler"""
    
    def __init__(self):
        self.providers = {
            'openai': OpenAIProvider,
            'claude': AnthropicProvider,
            'gemini': GoogleProvider
        }
    
    def get_user_api_key(self, user_id: str, provider: str) -> Optional[str]:
        """Retrieve and decrypt user's API key for a specific provider"""
        try:
            response = table.get_item(Key={'userId': user_id})
            if 'Item' not in response:
                return None
            
            encrypted_key = response['Item'].get(f'{provider}_api_key')
            if not encrypted_key:
                return None
            
            # Decrypt the API key using KMS
            decrypt_response = kms.decrypt(
                CiphertextBlob=encrypted_key,
                KeyId=kms_key_id
            )
            return decrypt_response['Plaintext'].decode('utf-8')
            
        except ClientError as e:
            logger.error(f"Error retrieving API key: {str(e)}")
            return None
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's default provider and other preferences"""
        try:
            response = table.get_item(Key={'userId': user_id})
            if 'Item' not in response:
                return {'default_provider': None, 'session_context': ''}
            
            return {
                'default_provider': response['Item'].get('default_provider'),
                'session_context': response['Item'].get('session_context', '')
            }
        except ClientError as e:
            logger.error(f"Error retrieving user preferences: {str(e)}")
            return {'default_provider': None, 'session_context': ''}
    
    def update_session_context(self, user_id: str, context: str):
        """Update user's session context"""
        try:
            table.update_item(
                Key={'userId': user_id},
                UpdateExpression='SET session_context = :context',
                ExpressionAttributeValues={':context': context}
            )
        except ClientError as e:
            logger.error(f"Error updating session context: {str(e)}")
    
    def handle_llm_query(self, user_id: str, query: str, provider: str = None) -> str:
        """Handle LLM query with specified or default provider"""
        try:
            # Get user preferences
            preferences = self.get_user_preferences(user_id)
            if not provider:
                provider = preferences['default_provider']
            
            if not provider:
                return "Please set a default provider or specify which AI to use. Say 'Set OpenAI as my default' or 'Ask Gemini, your question here'."
            
            # Get API key for the provider
            api_key = self.get_user_api_key(user_id, provider)
            if not api_key:
                return f"Your {provider} API key is not linked. Please check the Alexa app for instructions on how to link your key."
            
            # Initialize provider
            if provider not in self.providers:
                return f"Provider {provider} is not supported."
            
            llm_provider = self.providers[provider](api_key)
            
            # Get session context
            context = preferences['session_context']
            
            # Generate response
            response = llm_provider.generate_response(query, context)
            
            # Update session context with the conversation
            new_context = f"{context}\nUser: {query}\nAssistant: {response}"
            self.update_session_context(user_id, new_context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling LLM query: {str(e)}")
            return "Sorry, I encountered an error processing your request."
    
    def set_default_provider(self, user_id: str, provider: str) -> str:
        """Set user's default provider"""
        try:
            if provider not in self.providers:
                return f"Provider {provider} is not supported. Available providers are: OpenAI, Claude, and Gemini."
            
            table.update_item(
                Key={'userId': user_id},
                UpdateExpression='SET default_provider = :provider',
                ExpressionAttributeValues={':provider': provider}
            )
            return f"Okay, {provider} is now your default provider. You can now just ask your question."
        except ClientError as e:
            logger.error(f"Error setting default provider: {str(e)}")
            return "Sorry, I encountered an error setting your default provider."
    
    def clear_context(self, user_id: str) -> str:
        """Clear user's session context"""
        try:
            table.update_item(
                Key={'userId': user_id},
                UpdateExpression='SET session_context = :empty',
                ExpressionAttributeValues={':empty': ''}
            )
            return "Session context cleared. Starting a new conversation."
        except ClientError as e:
            logger.error(f"Error clearing context: {str(e)}")
            return "Sorry, I encountered an error clearing your session."

def lambda_handler(event, context):
    """Main Lambda handler for Alexa Skill"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Initialize skill handler
        skill = AIAssistantSkill()
        
        # Extract user ID and intent
        user_id = event['session']['user']['userId']
        intent_name = event['request']['intent']['name']
        
        if intent_name == 'LLMQueryIntent':
            # Handle LLM query (uses default provider)
            query = event['request']['intent']['slots']['Query']['value']
            response_text = skill.handle_llm_query(user_id, query)
            
        elif intent_name == 'LLMQueryWithProviderIntent':
            # Handle LLM query with specific provider
            query = event['request']['intent']['slots']['Query']['value']
            provider = event['request']['intent']['slots']['Provider']['value'].lower()
            response_text = skill.handle_llm_query(user_id, query, provider)
            
        elif intent_name == 'SetDefaultProviderIntent':
            # Set default provider
            provider = event['request']['intent']['slots']['Provider']['value'].lower()
            response_text = skill.set_default_provider(user_id, provider)
            
        elif intent_name == 'ClearContextIntent':
            # Clear session context
            response_text = skill.clear_context(user_id)
            
        elif intent_name == 'AMAZON.HelpIntent':
            # Provide help
            response_text = "AI Assistant Pro allows you to interact with multiple AI providers. You can say 'Ask OpenAI, what is the capital of France?' or set a default provider by saying 'Set Claude as my default'. To link your API keys, check the Alexa app for instructions."
            
        else:
            response_text = "I didn't understand that. You can ask me a question or say 'help' for instructions."
        
        # Return Alexa response
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
                    'text': 'Sorry, I encountered an error processing your request.'
                },
                'shouldEndSession': True
            }
        }
