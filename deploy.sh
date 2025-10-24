#!/bin/bash

# AI Assistant Pro Alexa Skill Deployment Script
# This script deploys the complete infrastructure using AWS CLI

set -e

# Configuration
STACK_NAME="ai-assistant-pro"
REGION="us-east-1"
ENVIRONMENT="dev"

echo "🚀 Starting AI Assistant Pro deployment..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

echo "✅ AWS CLI is configured"

# Deploy CloudFormation stack
echo "📦 Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file ai-assistant-infrastructure.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides Environment=$ENVIRONMENT \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

echo "✅ CloudFormation stack deployed"

# Get stack outputs
echo "📋 Getting stack outputs..."
DYNAMODB_TABLE=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`DynamoDBTableName`].OutputValue' \
    --output text \
    --region $REGION)

KMS_KEY_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`KMSKeyId`].OutputValue' \
    --output text \
    --region $REGION)

LAMBDA_FUNCTION_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionArn`].OutputValue' \
    --output text \
    --region $REGION)

echo "📊 Stack outputs:"
echo "  DynamoDB Table: $DYNAMODB_TABLE"
echo "  KMS Key ID: $KMS_KEY_ID"
echo "  Lambda Function ARN: $LAMBDA_FUNCTION_ARN"

# Create deployment package for Lambda function
echo "📦 Creating Lambda deployment package..."
mkdir -p lambda_package
cp lambda_function.py lambda_package/
cp requirements.txt lambda_package/

# Install dependencies
cd lambda_package
pip install -r requirements.txt -t .
zip -r ../lambda_function.zip .
cd ..
rm -rf lambda_package

# Update Lambda function code
echo "🔄 Updating Lambda function code..."
aws lambda update-function-code \
    --function-name ai-assistant-alexa-skill-$ENVIRONMENT \
    --zip-file fileb://lambda_function.zip \
    --region $REGION

echo "✅ Lambda function updated"

# Create deployment package for web portal
echo "📦 Creating web portal deployment package..."
mkdir -p web_portal_package
cp web_portal.py web_portal_package/
cp requirements.txt web_portal_package/

# Install dependencies
cd web_portal_package
pip install -r requirements.txt -t .
zip -r ../web_portal.zip .
cd ..
rm -rf web_portal_package

# Update web portal Lambda function code
echo "🔄 Updating web portal Lambda function code..."
aws lambda update-function-code \
    --function-name ai-assistant-web-portal-$ENVIRONMENT \
    --zip-file fileb://web_portal.zip \
    --region $REGION

echo "✅ Web portal Lambda function updated"

# Create API Gateway integration
echo "🌐 Setting up API Gateway..."
API_ID=$(aws apigateway get-rest-apis \
    --query "items[?name=='ai-assistant-web-portal-$ENVIRONMENT'].id" \
    --output text \
    --region $REGION)

if [ "$API_ID" = "None" ] || [ -z "$API_ID" ]; then
    echo "Creating new API Gateway..."
    API_ID=$(aws apigateway create-rest-api \
        --name ai-assistant-web-portal-$ENVIRONMENT \
        --description "API Gateway for AI Assistant Pro web portal" \
        --query 'id' \
        --output text \
        --region $REGION)
fi

echo "API Gateway ID: $API_ID"

# Get root resource ID
ROOT_RESOURCE_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --query 'items[?path==`/`].id' \
    --output text \
    --region $REGION)

# Create proxy resource
aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_RESOURCE_ID \
    --path-part '{proxy+}' \
    --region $REGION

echo "✅ API Gateway configured"

# Clean up deployment packages
rm -f lambda_function.zip web_portal.zip

echo "🎉 Deployment completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Create your Alexa Skill in the Alexa Developer Console"
echo "2. Configure the skill to use Lambda function: $LAMBDA_FUNCTION_ARN"
echo "3. Set up the interaction model with the intents defined in the PRD"
echo "4. Test the skill with your API keys"
echo ""
echo "🔗 Web portal will be available at the API Gateway endpoint"
echo "📊 DynamoDB table: $DYNAMODB_TABLE"
echo "🔐 KMS Key ID: $KMS_KEY_ID"
