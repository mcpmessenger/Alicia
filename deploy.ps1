# AI Assistant Pro Alexa Skill Deployment Script (PowerShell)
# This script deploys the complete infrastructure using AWS CLI

param(
    [string]$StackName = "ai-assistant-pro",
    [string]$Region = "us-east-1",
    [string]$Environment = "dev"
)

Write-Host "🚀 Starting AI Assistant Pro deployment..." -ForegroundColor Green

# Check if AWS CLI is configured
try {
    $callerIdentity = aws sts get-caller-identity 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "AWS CLI not configured"
    }
    Write-Host "✅ AWS CLI is configured" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI is not configured. Please run 'aws configure' first." -ForegroundColor Red
    exit 1
}

# Deploy CloudFormation stack
Write-Host "📦 Deploying CloudFormation stack..." -ForegroundColor Yellow
try {
    aws cloudformation deploy `
        --template-file ai-assistant-infrastructure.yaml `
        --stack-name $StackName `
        --parameter-overrides Environment=$Environment `
        --capabilities CAPABILITY_NAMED_IAM `
        --region $Region
    
    if ($LASTEXITCODE -ne 0) {
        throw "CloudFormation deployment failed"
    }
    Write-Host "✅ CloudFormation stack deployed" -ForegroundColor Green
} catch {
    Write-Host "❌ CloudFormation deployment failed" -ForegroundColor Red
    exit 1
}

# Get stack outputs
Write-Host "📋 Getting stack outputs..." -ForegroundColor Yellow
try {
    $dynamoDbTable = aws cloudformation describe-stacks `
        --stack-name $StackName `
        --query 'Stacks[0].Outputs[?OutputKey==`DynamoDBTableName`].OutputValue' `
        --output text `
        --region $Region

    $kmsKeyId = aws cloudformation describe-stacks `
        --stack-name $StackName `
        --query 'Stacks[0].Outputs[?OutputKey==`KMSKeyId`].OutputValue' `
        --output text `
        --region $Region

    $lambdaFunctionArn = aws cloudformation describe-stacks `
        --stack-name $StackName `
        --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionArn`].OutputValue' `
        --output text `
        --region $Region

    Write-Host "📊 Stack outputs:" -ForegroundColor Cyan
    Write-Host "  DynamoDB Table: $dynamoDbTable" -ForegroundColor White
    Write-Host "  KMS Key ID: $kmsKeyId" -ForegroundColor White
    Write-Host "  Lambda Function ARN: $lambdaFunctionArn" -ForegroundColor White
} catch {
    Write-Host "❌ Failed to get stack outputs" -ForegroundColor Red
    exit 1
}

# Create deployment package for Lambda function
Write-Host "📦 Creating Lambda deployment package..." -ForegroundColor Yellow
try {
    # Create temporary directory
    $tempDir = "lambda_package"
    if (Test-Path $tempDir) {
        Remove-Item -Recurse -Force $tempDir
    }
    New-Item -ItemType Directory -Path $tempDir | Out-Null
    
    # Copy files
    Copy-Item "lambda_function.py" $tempDir
    Copy-Item "requirements.txt" $tempDir
    
    # Install dependencies
    Set-Location $tempDir
    pip install -r requirements.txt -t . --quiet
    
    # Create zip file
    Compress-Archive -Path * -DestinationPath "../lambda_function.zip" -Force
    Set-Location ..
    Remove-Item -Recurse -Force $tempDir
    
    Write-Host "✅ Lambda deployment package created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create Lambda deployment package" -ForegroundColor Red
    exit 1
}

# Update Lambda function code
Write-Host "🔄 Updating Lambda function code..." -ForegroundColor Yellow
try {
    aws lambda update-function-code `
        --function-name "ai-assistant-alexa-skill-$Environment" `
        --zip-file fileb://lambda_function.zip `
        --region $Region
    
    if ($LASTEXITCODE -ne 0) {
        throw "Lambda update failed"
    }
    Write-Host "✅ Lambda function updated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to update Lambda function" -ForegroundColor Red
    exit 1
}

# Create deployment package for web portal
Write-Host "📦 Creating web portal deployment package..." -ForegroundColor Yellow
try {
    # Create temporary directory
    $tempDir = "web_portal_package"
    if (Test-Path $tempDir) {
        Remove-Item -Recurse -Force $tempDir
    }
    New-Item -ItemType Directory -Path $tempDir | Out-Null
    
    # Copy files
    Copy-Item "web_portal.py" $tempDir
    Copy-Item "requirements.txt" $tempDir
    
    # Install dependencies
    Set-Location $tempDir
    pip install -r requirements.txt -t . --quiet
    
    # Create zip file
    Compress-Archive -Path * -DestinationPath "../web_portal.zip" -Force
    Set-Location ..
    Remove-Item -Recurse -Force $tempDir
    
    Write-Host "✅ Web portal deployment package created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create web portal deployment package" -ForegroundColor Red
    exit 1
}

# Update web portal Lambda function code
Write-Host "🔄 Updating web portal Lambda function code..." -ForegroundColor Yellow
try {
    aws lambda update-function-code `
        --function-name "ai-assistant-web-portal-$Environment" `
        --zip-file fileb://web_portal.zip `
        --region $Region
    
    if ($LASTEXITCODE -ne 0) {
        throw "Web portal Lambda update failed"
    }
    Write-Host "✅ Web portal Lambda function updated" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to update web portal Lambda function" -ForegroundColor Red
    exit 1
}

# Clean up deployment packages
Remove-Item -Force "lambda_function.zip" -ErrorAction SilentlyContinue
Remove-Item -Force "web_portal.zip" -ErrorAction SilentlyContinue

Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Create your Alexa Skill in the Alexa Developer Console" -ForegroundColor White
Write-Host "2. Configure the skill to use Lambda function: $lambdaFunctionArn" -ForegroundColor White
Write-Host "3. Set up the interaction model with the intents defined in the PRD" -ForegroundColor White
Write-Host "4. Test the skill with your API keys" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Web portal will be available at the API Gateway endpoint" -ForegroundColor Cyan
Write-Host "📊 DynamoDB table: $dynamoDbTable" -ForegroundColor White
Write-Host "🔐 KMS Key ID: $kmsKeyId" -ForegroundColor White
