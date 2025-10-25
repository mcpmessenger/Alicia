import json
import boto3
import os
import logging
import urllib.request
import urllib.parse
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE', 'ai-assistant-users-dev'))

def get_alexa_app_html():
    """Return the Alexa app portal HTML"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant Pro - Alexa App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: white;
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .header p {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1rem;
        }

        .alexa-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .alexa-card h3 {
            color: white;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }

        .alexa-card p {
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.6;
            margin-bottom: 15px;
        }

        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            border-radius: 10px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 15px;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        .status {
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: 500;
        }

        .status.success {
            background: rgba(76, 175, 80, 0.2);
            border: 1px solid rgba(76, 175, 80, 0.3);
            color: #4CAF50;
        }

        .status.error {
            background: rgba(244, 67, 54, 0.2);
            border: 1px solid rgba(244, 67, 54, 0.3);
            color: #f44336;
        }

        .hidden {
            display: none;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            color: white;
            margin-bottom: 8px;
            font-weight: 500;
        }

        .form-group input {
            width: 100%;
            padding: 12px 16px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 16px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }

        .form-group input:focus {
            outline: none;
            border-color: rgba(255, 255, 255, 0.5);
            background: rgba(255, 255, 255, 0.2);
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
        }

        .form-group input::placeholder {
            color: rgba(255, 255, 255, 0.6);
        }

        .instructions {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .instructions h3 {
            color: white;
            margin-bottom: 10px;
        }

        .instructions p {
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.6;
        }

        .instructions ol {
            color: rgba(255, 255, 255, 0.8);
            margin-left: 20px;
            margin-top: 10px;
        }

        .instructions li {
            margin-bottom: 8px;
        }

        .voice-commands {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }

        .voice-commands h3 {
            color: white;
            margin-bottom: 15px;
        }

        .command {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
            color: rgba(255, 255, 255, 0.9);
        }

        .command strong {
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎤 AI Assistant Pro</h1>
            <p>Your personal AI assistant for Alexa</p>
        </div>

        <!-- Main Portal -->
        <div id="mainPortal">
            <div class="alexa-card">
                <h3>📱 Alexa App Integration</h3>
                <p>Connect your Alexa device to AI Assistant Pro for voice-controlled AI interactions.</p>
                
                <div class="instructions">
                    <h3>🔧 Setup Instructions</h3>
                    <ol>
                        <li>Open the Alexa app on your phone</li>
                        <li>Go to Skills & Games</li>
                        <li>Search for "AI Assistant Pro"</li>
                        <li>Enable the skill</li>
                        <li>Link your account using the code below</li>
                    </ol>
                </div>

                <div class="form-group">
                    <label for="alexaUserId">Your Alexa User ID</label>
                    <input type="text" id="alexaUserId" placeholder="Enter your Alexa User ID" />
                    <small style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">
                        Find this in your Alexa app under Settings → Account
                    </small>
                </div>

                <button class="btn" onclick="linkAlexaAccount()">Link Alexa Account</button>
            </div>

            <div class="alexa-card">
                <h3>🔑 API Key Management</h3>
                <p>Configure your AI provider API keys to enable voice interactions.</p>
                
                <div class="form-group">
                    <label for="openaiKey">OpenAI API Key</label>
                    <input type="password" id="openaiKey" placeholder="Enter your OpenAI API key (sk-...)" />
                </div>

                <div class="form-group">
                    <label for="geminiKey">Google Gemini API Key</label>
                    <input type="password" id="geminiKey" placeholder="Enter your Gemini API key (AI...)" />
                </div>

                <div class="form-group">
                    <label for="claudeKey">Anthropic Claude API Key</label>
                    <input type="password" id="claudeKey" placeholder="Enter your Claude API key (sk-ant-...)" />
                </div>

                <button class="btn" onclick="saveApiKeys()">Save API Keys</button>
            </div>

            <div class="voice-commands">
                <h3>🎤 Voice Commands</h3>
                <div class="command">
                    <strong>"Alexa, open AI Assistant Pro"</strong> - Launch the skill
                </div>
                <div class="command">
                    <strong>"Ask OpenAI, what is machine learning?"</strong> - Query specific provider
                </div>
                <div class="command">
                    <strong>"Ask Gemini, tell me about space"</strong> - Use Google Gemini
                </div>
                <div class="command">
                    <strong>"Ask Claude, explain quantum computing"</strong> - Use Anthropic Claude
                </div>
                <div class="command">
                    <strong>"Set Claude as my default"</strong> - Set default provider
                </div>
                <div class="command">
                    <strong>"What is artificial intelligence?"</strong> - Use default provider
                </div>
                <div class="command">
                    <strong>"Start a new conversation"</strong> - Clear context
                </div>
            </div>
        </div>

        <!-- Success State -->
        <div id="successState" class="hidden">
            <div class="alexa-card">
                <h3>✅ Setup Complete!</h3>
                <p>Your Alexa account has been successfully linked to AI Assistant Pro.</p>
                <p>You can now use voice commands to interact with your AI providers.</p>
                
                <button class="btn" onclick="showMainPortal()">Back to Portal</button>
            </div>
        </div>

        <div id="status" class="status hidden"></div>
    </div>

    <script>
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = `status ${type}`;
            status.classList.remove('hidden');
            setTimeout(() => {
                status.classList.add('hidden');
            }, 5000);
        }

        function showMainPortal() {
            document.getElementById('mainPortal').classList.remove('hidden');
            document.getElementById('successState').classList.add('hidden');
        }

        function showSuccessState() {
            document.getElementById('mainPortal').classList.add('hidden');
            document.getElementById('successState').classList.remove('hidden');
        }

        async function linkAlexaAccount() {
            const alexaUserId = document.getElementById('alexaUserId').value;

            if (!alexaUserId) {
                showStatus('Please enter your Alexa User ID', 'error');
                return;
            }

            try {
                const response = await fetch('/api/link-alexa', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ alexaUserId })
                });

                const data = await response.json();

                if (data.success) {
                    showStatus('Alexa account linked successfully!', 'success');
                    showSuccessState();
                } else {
                    showStatus(data.message || 'Failed to link Alexa account', 'error');
                }
            } catch (error) {
                showStatus('Network error. Please try again.', 'error');
            }
        }

        async function saveApiKeys() {
            const openaiKey = document.getElementById('openaiKey').value;
            const geminiKey = document.getElementById('geminiKey').value;
            const claudeKey = document.getElementById('claudeKey').value;

            if (!openaiKey && !geminiKey && !claudeKey) {
                showStatus('Please enter at least one API key', 'error');
                return;
            }

            try {
                const response = await fetch('/api/save-keys', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        openaiKey,
                        geminiKey,
                        claudeKey
                    })
                });

                const data = await response.json();

                if (data.success) {
                    showStatus('API keys saved successfully!', 'success');
                } else {
                    showStatus(data.message || 'Failed to save API keys', 'error');
                }
            } catch (error) {
                showStatus('Network error. Please try again.', 'error');
            }
        }
    </script>
</body>
</html>
"""

def lambda_handler(event, context):
    """Alexa app portal Lambda handler"""
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse the request
        if 'requestContext' in event:
            # Lambda Function URL
            http_method = event['requestContext']['http']['method']
            path = event['rawPath']
        else:
            # API Gateway
            http_method = event['httpMethod']
            path = event['path']
        
        logger.info(f"HTTP Method: {http_method}, Path: {path}")
        
        # Handle CORS
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        }
        
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # Route requests
        if path == '/' and http_method == 'GET':
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'text/html'},
                'body': get_alexa_app_html()
            }
        
        elif path == '/api/link-alexa' and http_method == 'POST':
            return handle_link_alexa(event)
        
        elif path == '/api/save-keys' and http_method == 'POST':
            return handle_save_keys(event)
        
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not found'})
            }
    
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_link_alexa(event):
    """Handle Alexa account linking"""
    try:
        body = json.loads(event['body'])
        alexa_user_id = body['alexaUserId']
        
        # Create or update user record
        table.put_item(Item={
            'userId': alexa_user_id,
            'linked_at': datetime.utcnow().isoformat(),
            'default_provider': 'gemini'  # Default to Gemini for testing
        })
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'message': 'Alexa account linked successfully'
            })
        }
    
    except Exception as e:
        logger.error(f"Error in handle_link_alexa: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'message': 'Internal server error'})
        }

def handle_save_keys(event):
    """Handle API key saving"""
    try:
        body = json.loads(event['body'])
        
        # Get Alexa User ID from headers or body
        alexa_user_id = body.get('alexaUserId', 'default-user')
        
        # Prepare update expression
        update_expression = 'SET updated_at = :time'
        expression_values = {':time': datetime.utcnow().isoformat()}
        
        if body.get('openaiKey'):
            update_expression += ', openai_api_key = :openai'
            expression_values[':openai'] = body['openaiKey']
        
        if body.get('geminiKey'):
            update_expression += ', gemini_api_key = :gemini'
            expression_values[':gemini'] = body['geminiKey']
        
        if body.get('claudeKey'):
            update_expression += ', claude_api_key = :claude'
            expression_values[':claude'] = body['claudeKey']
        
        # Update user record
        table.update_item(
            Key={'userId': alexa_user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'message': 'API keys saved successfully'
            })
        }
    
    except Exception as e:
        logger.error(f"Error in handle_save_keys: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'success': False, 'message': 'Internal server error'})
        }
