# create-lambda-function.ps1
# Create a new Lambda function for AI Pro Skill

Write-Host "Creating Lambda function for AI Pro Skill..." -ForegroundColor Cyan
Write-Host ""

$FUNCTION_NAME = "ai-pro-skill"
$REGION = "us-east-1"
$ROLE_NAME = "ai-pro-skill-role"

# Step 1: Create IAM role for Lambda
Write-Host "[1/4] Creating IAM role..." -ForegroundColor Yellow

$TRUST_POLICY = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"@

$TRUST_POLICY | Out-File -FilePath "trust-policy.json" -Encoding utf8

try {
    aws iam create-role `
        --role-name $ROLE_NAME `
        --assume-role-policy-document file://trust-policy.json `
        --region $REGION
    
    Write-Host "  [OK] Role created: $ROLE_NAME" -ForegroundColor Green
}
catch {
    Write-Host "  [INFO] Role may already exist" -ForegroundColor Yellow
}

# Attach basic Lambda execution policy
Write-Host "[2/4] Attaching policies..." -ForegroundColor Yellow

aws iam attach-role-policy `
    --role-name $ROLE_NAME `
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Attach DynamoDB policy
aws iam attach-role-policy `
    --role-name $ROLE_NAME `
    --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess

Write-Host "  [OK] Policies attached" -ForegroundColor Green

# Wait for role to propagate
Write-Host "[3/4] Waiting for IAM role to propagate (10 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Get AWS account ID
$ACCOUNT_ID = aws sts get-caller-identity --query 'Account' --output text
$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"

Write-Host "  [OK] Role ARN: $ROLE_ARN" -ForegroundColor Green

# Step 4: Create Lambda function
Write-Host "[4/4] Creating Lambda function..." -ForegroundColor Yellow

# Create a simple placeholder Lambda
$PLACEHOLDER_CODE = @"
def lambda_handler(event, context):
    return {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': 'AI Pro is being set up. Please wait a moment.'
            },
            'shouldEndSession': False
        }
    }
"@

$PLACEHOLDER_CODE | Out-File -FilePath "placeholder_lambda.py" -Encoding utf8

# Zip it
Compress-Archive -Path "placeholder_lambda.py" -DestinationPath "placeholder.zip" -Force

try {
    aws lambda create-function `
        --function-name $FUNCTION_NAME `
        --runtime python3.11 `
        --role $ROLE_ARN `
        --handler lambda_function.lambda_handler `
        --zip-file fileb://placeholder.zip `
        --timeout 30 `
        --memory-size 512 `
        --region $REGION `
        --environment "Variables={DYNAMODB_TABLE=ai-assistant-users-dev}"
    
    Write-Host "  [OK] Lambda function created!" -ForegroundColor Green
}
catch {
    Write-Host "  [ERROR] Failed to create function: $_" -ForegroundColor Red
    exit 1
}

# Cleanup
Remove-Item "trust-policy.json" -Force
Remove-Item "placeholder_lambda.py" -Force
Remove-Item "placeholder.zip" -Force

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Lambda Function Created!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Function Name: $FUNCTION_NAME" -ForegroundColor White
Write-Host "Region: $REGION" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Set your API keys:" -ForegroundColor White
Write-Host ""
Write-Host "     aws lambda update-function-configuration --function-name $FUNCTION_NAME --region $REGION --environment Variables='{OPENAI_API_KEY=your-key,GOOGLE_API_KEY=your-key,ANTHROPIC_API_KEY=your-key,DYNAMODB_TABLE=ai-assistant-users-dev}'" -ForegroundColor Yellow
Write-Host ""
Write-Host "  2. Deploy your code:" -ForegroundColor White
Write-Host ""
Write-Host "     .\deploy-friendly-chat.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "  3. Connect to Alexa Skill in the Developer Console" -ForegroundColor White
Write-Host ""

