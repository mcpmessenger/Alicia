import json
import boto3
import os
import base64
import uuid
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
kms = boto3.client('kms')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
kms_key_id = os.environ['KMS_KEY_ID']

def generate_token() -> str:
    """Generate a unique token for API key configuration"""
    return str(uuid.uuid4())

def store_token(user_id: str, token: str, expires_in_hours: int = 24):
    """Store configuration token in DynamoDB"""
    try:
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        table.put_item(
            Item={
                'userId': f"token_{token}",
                'user_id': user_id,
                'expires_at': int(expires_at.timestamp()),
                'token_type': 'api_key_config'
            }
        )
        logger.info(f"Token stored for user {user_id}")
    except ClientError as e:
        logger.error(f"Error storing token: {str(e)}")
        raise

def validate_token(token: str) -> str:
    """Validate token and return user ID"""
    try:
        response = table.get_item(Key={'userId': f"token_{token}"})
        if 'Item' not in response:
            return None
        
        item = response['Item']
        expires_at = item.get('expires_at', 0)
        
        if datetime.utcnow().timestamp() > expires_at:
            # Token expired, clean up
            table.delete_item(Key={'userId': f"token_{token}"})
            return None
        
        return item['user_id']
    except ClientError as e:
        logger.error(f"Error validating token: {str(e)}")
        return None

def encrypt_api_key(api_key: str) -> bytes:
    """Encrypt API key using KMS"""
    try:
        response = kms.encrypt(
            KeyId=kms_key_id,
            Plaintext=api_key
        )
        return response['CiphertextBlob']
    except ClientError as e:
        logger.error(f"Error encrypting API key: {str(e)}")
        raise

def store_api_key(user_id: str, provider: str, encrypted_key: bytes):
    """Store encrypted API key in DynamoDB"""
    try:
        table.update_item(
            Key={'userId': user_id},
            UpdateExpression=f'SET {provider}_api_key = :key',
            ExpressionAttributeValues={':key': encrypted_key}
        )
        logger.info(f"API key stored for user {user_id}, provider {provider}")
    except ClientError as e:
        logger.error(f"Error storing API key: {str(e)}")
        raise

def get_configuration_page():
    """Return the HTML configuration page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Assistant Pro - API Key Configuration</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .provider-section {
                margin-bottom: 30px;
                padding: 20px;
                border: 2px solid #f0f0f0;
                border-radius: 8px;
            }
            .provider-section h3 {
                margin-top: 0;
                color: #555;
            }
            input[type="text"] {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
                margin-bottom: 10px;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
                width: 100%;
                margin-top: 10px;
            }
            button:hover {
                background: #5a6fd8;
            }
            .status {
                padding: 10px;
                border-radius: 6px;
                margin-top: 10px;
                display: none;
            }
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .instructions {
                background: #e7f3ff;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
                border-left: 4px solid #007bff;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔑 AI Assistant Pro - API Key Configuration</h1>
            
            <div class="instructions">
                <strong>Instructions:</strong> Enter your API keys for the AI providers you want to use. 
                Your keys are encrypted and stored securely. You only need to configure the providers you plan to use.
            </div>
            
            <form id="configForm">
                <div class="provider-section">
                    <h3>🤖 OpenAI (GPT-4, GPT-3.5)</h3>
                    <input type="text" id="openai_key" placeholder="sk-..." />
                    <button type="button" onclick="saveKey('openai')">Save OpenAI Key</button>
                    <div id="openai_status" class="status"></div>
                </div>
                
                <div class="provider-section">
                    <h3>🧠 Anthropic Claude</h3>
                    <input type="text" id="claude_key" placeholder="sk-ant-..." />
                    <button type="button" onclick="saveKey('claude')">Save Claude Key</button>
                    <div id="claude_status" class="status"></div>
                </div>
                
                <div class="provider-section">
                    <h3>🔍 Google Gemini</h3>
                    <input type="text" id="gemini_key" placeholder="AI..." />
                    <button type="button" onclick="saveKey('gemini')">Save Gemini Key</button>
                    <div id="gemini_status" class="status"></div>
                </div>
            </form>
        </div>
        
        <script>
            function showStatus(provider, message, isError = false) {
                const statusEl = document.getElementById(provider + '_status');
                statusEl.textContent = message;
                statusEl.className = 'status ' + (isError ? 'error' : 'success');
                statusEl.style.display = 'block';
            }
            
            async function saveKey(provider) {
                const keyInput = document.getElementById(provider + '_key');
                const apiKey = keyInput.value.trim();
                
                if (!apiKey) {
                    showStatus(provider, 'Please enter a valid API key', true);
                    return;
                }
                
                try {
                    const response = await fetch('/api/save-key', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            provider: provider,
                            api_key: apiKey
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showStatus(provider, '✅ API key saved successfully!');
                        keyInput.value = '';
                    } else {
                        showStatus(provider, '❌ Error: ' + result.error, true);
                    }
                } catch (error) {
                    showStatus(provider, '❌ Network error: ' + error.message, true);
                }
            }
        </script>
    </body>
    </html>
    """

def lambda_handler(event, context):
    """Main Lambda handler for web portal"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Handle different HTTP methods and paths
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        if http_method == 'GET' and path == '/':
            # Return configuration page
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': get_configuration_page()
            }
        
        elif http_method == 'POST' and path == '/api/save-key':
            # Handle API key saving
            try:
                body = json.loads(event.get('body', '{}'))
                provider = body.get('provider')
                api_key = body.get('api_key')
                
                if not provider or not api_key:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Provider and API key are required'})
                    }
                
                # For demo purposes, we'll use a placeholder user ID
                # In production, this should be extracted from the token
                user_id = "demo_user_123"
                
                # Encrypt and store the API key
                encrypted_key = encrypt_api_key(api_key)
                store_api_key(user_id, provider, encrypted_key)
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'message': 'API key saved successfully'})
                }
                
            except Exception as e:
                logger.error(f"Error saving API key: {str(e)}")
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Internal server error'})
                }
        
        else:
            # 404 for unknown paths
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'text/html',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': '<html><body><h1>404 - Page Not Found</h1></body></html>'
            }
            
    except Exception as e:
        logger.error(f"Error in web portal handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'text/html',
                'Access-Control-Allow-Origin': '*'
            },
            'body': '<html><body><h1>500 - Internal Server Error</h1></body></html>'
        }
