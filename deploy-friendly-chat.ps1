# deploy-friendly-chat.ps1
# Deploy AI Pro as a Friendly Chat Assistant with Gemini, OpenAI and Anthropic

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Pro Friendly Chat Deployment" -ForegroundColor Cyan
Write-Host "  Research Assistant with AI Chat" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$FUNCTION_NAME = "ai-pro-alexa-skill"
$REGION = "us-east-1"

Write-Host "[1/5] Creating deployment package..." -ForegroundColor Yellow

# Create temp directory
$TEMP_DIR = "lambda-friendly-chat-temp"
if (Test-Path $TEMP_DIR) {
    Remove-Item -Recurse -Force $TEMP_DIR
}
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null

# Copy Lambda function
Write-Host "  - Copying lambda_ai_pro_friendly_chat.py..." -ForegroundColor Gray
Copy-Item "lambda_ai_pro_friendly_chat.py" "$TEMP_DIR\lambda_function.py"

# Copy shopping tools
Write-Host "  - Copying shopping_tools.py..." -ForegroundColor Gray
Copy-Item "shopping_tools.py" "$TEMP_DIR\shopping_tools.py"

Write-Host "[2/5] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "  - boto3 (AWS SDK)" -ForegroundColor Gray

# Install dependencies (boto3 is already in Lambda, but we'll include it anyway)
pip install --target $TEMP_DIR boto3 -q

Write-Host "[3/5] Creating deployment ZIP..." -ForegroundColor Yellow
$ZIP_FILE = "lambda-friendly-chat.zip"
if (Test-Path $ZIP_FILE) {
    Remove-Item $ZIP_FILE
}

# Create ZIP
Compress-Archive -Path "$TEMP_DIR\*" -DestinationPath $ZIP_FILE -Force
Write-Host "  [OK] Created $ZIP_FILE" -ForegroundColor Green

Write-Host "[4/5] Uploading to AWS Lambda..." -ForegroundColor Yellow
Write-Host "  Function: $FUNCTION_NAME" -ForegroundColor Gray
Write-Host "  Region: $REGION" -ForegroundColor Gray

try {
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://$ZIP_FILE `
        --region $REGION `
        --output json | Out-Null
    
    Write-Host "  [OK] Lambda function updated!" -ForegroundColor Green
}
catch {
    Write-Host "  [ERROR] Error uploading to Lambda: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "  1. AWS CLI is configured (run: aws configure)" -ForegroundColor Yellow
    Write-Host "  2. Lambda function '$FUNCTION_NAME' exists" -ForegroundColor Yellow
    Write-Host "  3. You have permission to update Lambda functions" -ForegroundColor Yellow
    exit 1
}

Write-Host "[5/5] Cleaning up..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $TEMP_DIR
Write-Host "  [OK] Cleanup complete" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your AI Pro skill is now a friendly chat assistant!" -ForegroundColor Green
Write-Host ""
Write-Host "What Changed:" -ForegroundColor Cyan
Write-Host "  - Friendly, casual personality focused on research and conversation" -ForegroundColor White
Write-Host "  - Integrated with Gemini, OpenAI and Anthropic for rich discussions" -ForegroundColor White
Write-Host "  - Shopping is now subtle/secondary (only when explicitly requested)" -ForegroundColor White
Write-Host "  - Great for discussing science, history, tech, and any topic!" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Verify API keys are set in Lambda environment variables" -ForegroundColor White
Write-Host "  2. Test your skill in the Alexa Developer Console" -ForegroundColor White
Write-Host "  3. Try: 'Alexa, open AI Pro' then ask questions!" -ForegroundColor White
Write-Host ""
Write-Host "Example Queries:" -ForegroundColor Cyan
Write-Host "  - 'Tell me about quantum physics'" -ForegroundColor White
Write-Host "  - 'What happened in 1969?'" -ForegroundColor White
Write-Host "  - 'Use Gemini to explain black holes'" -ForegroundColor White
Write-Host "  - 'What's the latest in AI technology?'" -ForegroundColor White
Write-Host "  - 'Find me wireless headphones' (shopping still works!)" -ForegroundColor White
Write-Host ""
Write-Host "API Key Check:" -ForegroundColor Cyan
Write-Host "  Run this to verify your API keys are set:" -ForegroundColor White
Write-Host ""
Write-Host "  aws lambda get-function-configuration --function-name $FUNCTION_NAME --region $REGION --query 'Environment.Variables'" -ForegroundColor Yellow
Write-Host ""
Write-Host "Happy chatting!" -ForegroundColor Cyan
Write-Host ""
