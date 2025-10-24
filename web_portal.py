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
    with open('web-portal.html', 'r') as f:
        return f.read()

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
