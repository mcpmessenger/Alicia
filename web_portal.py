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
    """Return the modern glassmorphism HTML configuration page"""
    # Return a simple HTML page for now
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Assistant Pro - API Configuration</title>
        <style>
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
                min-height: 100vh;
                color: #e0e6ed;
                margin: 0;
                padding: 2rem;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            .card {
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 2rem;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            .header {
                text-align: center;
                margin-bottom: 2rem;
            }
            .logo {
                font-size: 2.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .form-group {
                margin-bottom: 1.5rem;
            }
            .label {
                display: block;
                font-size: 0.9rem;
                font-weight: 500;
                color: #cbd5e0;
                margin-bottom: 0.5rem;
            }
            .input {
                width: 100%;
                padding: 0.875rem 1rem;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: #f7fafc;
                font-size: 0.95rem;
                box-sizing: border-box;
            }
            .input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                padding: 0.875rem 2rem;
                border-radius: 12px;
                color: white;
                font-weight: 600;
                font-size: 0.95rem;
                cursor: pointer;
                width: 100%;
                margin-top: 1rem;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            }
            .status {
                padding: 1rem;
                border-radius: 12px;
                margin-bottom: 1rem;
                display: none;
            }
            .status.success {
                background: rgba(56, 178, 172, 0.1);
                border: 1px solid rgba(56, 178, 172, 0.3);
                color: #68d391;
            }
            .status.error {
                background: rgba(245, 101, 101, 0.1);
                border: 1px solid rgba(245, 101, 101, 0.3);
                color: #fc8181;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="logo">AI Assistant Pro</h1>
                <p>Configure your API keys for seamless AI interactions</p>
            </div>
            
            <div class="card">
                <h2>API Configuration</h2>
                
                <div class="status" id="status"></div>
                
                <form id="apiForm">
                    <div class="form-group">
                        <label class="label" for="provider">Provider</label>
                        <select id="provider" class="input" required>
                            <option value="">Select a provider</option>
                            <option value="openai">OpenAI (GPT-3.5 & GPT-4)</option>
                            <option value="claude">Claude (Anthropic)</option>
                            <option value="gemini">Gemini (Google)</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label class="label" for="apiKey">API Key</label>
                        <input type="password" id="apiKey" class="input" placeholder="Enter your API key" required>
                    </div>
                    
                    <div class="form-group">
                        <label class="label" for="userId">User ID</label>
                        <input type="text" id="userId" class="input" placeholder="Your Alexa User ID" required>
                    </div>
                    
                    <button type="submit" class="btn">Save API Key</button>
                </form>
            </div>
        </div>
        
        <script>
            document.getElementById('apiForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const provider = document.getElementById('provider').value;
                const apiKey = document.getElementById('apiKey').value;
                const userId = document.getElementById('userId').value;
                
                if (!provider || !apiKey || !userId) {
                    showStatus('Please fill in all fields', 'error');
                    return;
                }
                
                try {
                    const response = await fetch('/api/configure', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            provider: provider,
                            apiKey: apiKey,
                            userId: userId
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showStatus(`API key for ${provider} saved successfully!`, 'success');
                        document.getElementById('apiForm').reset();
                    } else {
                        showStatus(result.error || 'Failed to save API key', 'error');
                    }
                } catch (error) {
                    showStatus('Network error. Please try again.', 'error');
                }
            });
            
            function showStatus(message, type) {
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = `status ${type}`;
                status.style.display = 'block';
            }
        </script>
    </body>
    </html>
    """

def lambda_handler(event, context):
    """Main Lambda handler for web portal"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Handle Lambda Function URL format
        http_method = event.get('requestContext', {}).get('http', {}).get('method', 'GET')
        path = event.get('rawPath', '/')
        
        # Fallback for API Gateway format
        if not http_method:
            http_method = event.get('httpMethod', 'GET')
        if path == '/':
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
        
        elif http_method == 'POST' and path == '/api/configure':
            # Handle modern API key configuration
            try:
                body = json.loads(event.get('body', '{}'))
                provider = body.get('provider')
                api_key = body.get('apiKey')
                user_id = body.get('userId')
                
                if not provider or not api_key or not user_id:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Provider, API key, and User ID are required'})
                    }
                
                # Encrypt and store the API key
                encrypted_key = encrypt_api_key(api_key)
                store_api_key(user_id, provider, encrypted_key)
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'message': f'API key for {provider} saved successfully'})
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
        
        elif http_method == 'POST' and path == '/api/save-key':
            # Handle legacy API key saving
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
