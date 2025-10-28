# web_portal_shopping.py
# Enhanced web portal Lambda function with shopping capabilities

import json
import boto3
import os
import logging
from shopping_tools import product_search_tool

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_configuration_page():
    """Return the HTML for the configuration page"""
    with open('web-portal-shopping.html', 'r') as f:
        return f.read()

def lambda_handler(event, context):
    """Enhanced web portal Lambda function with shopping support"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse the request
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # Handle different routes
        if path == '/api/configure':
            return handle_api_configure(event)
        elif path == '/api/shopping':
            return handle_shopping_search(event)
        elif path == '/api/shopping-results':
            return handle_shopping_results(event)
        else:
            # Return the main page
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/html',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
                },
                'body': get_configuration_page()
            }
    
    except Exception as e:
        logger.error(f"Error in web portal: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_api_configure(event):
    """Handle API key configuration requests"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        provider = body.get('provider')
        api_key = body.get('apiKey')
        user_id = body.get('userId')
        
        if not all([provider, api_key, user_id]):
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
        # Store in DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'ai-assistant-users-dev'))
        
        # Update user record
        table.update_item(
            Key={'userId': user_id},
            UpdateExpression=f'SET {provider}_api_key = :key',
            ExpressionAttributeValues={':key': api_key}
        )
        
        logger.info(f"Updated {provider} API key for user {user_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': f'API key for {provider} saved successfully'})
        }
        
    except Exception as e:
        logger.error(f"Error in API configuration: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to save API key'})
        }

def handle_shopping_search(event):
    """Handle shopping search requests"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        query = body.get('query')
        max_price = body.get('max_price')
        category = body.get('category')
        
        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Query is required'})
            }
        
        # Call the product search tool
        tool_output = product_search_tool(query, max_price, category)
        tool_data = json.loads(tool_output)
        
        logger.info(f"Shopping search completed: {tool_data.get('total_results', 0)} results")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': tool_output
        }
        
    except Exception as e:
        logger.error(f"Error in shopping search: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to search for products'})
        }

def handle_shopping_results(event):
    """Handle requests for shopping results from DynamoDB"""
    try:
        # Get user ID from query parameters
        user_id = event.get('queryStringParameters', {}).get('userId')
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'User ID is required'})
            }
        
        # Retrieve shopping results from DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'ai-assistant-users-dev'))
        
        response = table.get_item(Key={'userId': user_id})
        
        if 'Item' in response:
            shopping_results = response['Item'].get('shopping_results')
            if shopping_results:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': shopping_results
                }
        
        return {
            'statusCode': 404,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'No shopping results found'})
        }
        
    except Exception as e:
        logger.error(f"Error retrieving shopping results: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to retrieve shopping results'})
        }
