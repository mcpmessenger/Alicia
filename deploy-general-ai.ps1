# Deploy AI Pro General Assistant to AWS Lambda

Write-Host "🚀 Deploying AI Pro General Assistant..." -ForegroundColor Cyan

# Step 1: Package the Lambda function
Write-Host "`n📦 Packaging Lambda function..." -ForegroundColor Yellow
Compress-Archive -Path "lambda_ai_pro_general.py","shopping_tools.py" -DestinationPath "lambda-general-ai.zip" -Force

if (Test-Path "lambda-general-ai.zip") {
    Write-Host "✅ Package created successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create package" -ForegroundColor Red
    exit 1
}

# Step 2: Deploy to AWS Lambda
Write-Host "`n🌐 Deploying to AWS Lambda..." -ForegroundColor Yellow
aws lambda update-function-code `
    --function-name ai-pro-alexa-skill `
    --zip-file fileb://lambda-general-ai.zip

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Lambda function deployed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to deploy Lambda function" -ForegroundColor Red
    exit 1
}

# Step 3: Remind about environment variables
Write-Host "`n⚙️  Don't forget to set environment variables:" -ForegroundColor Cyan
Write-Host "   OPENAI_API_KEY=sk-your-key-here" -ForegroundColor White
Write-Host "   DYNAMODB_TABLE=ai-assistant-users-dev" -ForegroundColor White
Write-Host "   AMAZON_PARTNER_TAG=aipro00-20" -ForegroundColor White

Write-Host "`n🎉 Deployment complete!" -ForegroundColor Green
Write-Host "`n📝 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Add your OpenAI API key to Lambda environment variables" -ForegroundColor White
Write-Host "   2. Test in Alexa Developer Console: 'Alexa, open AI Pro'" -ForegroundColor White
Write-Host "   3. Try: 'What is artificial intelligence?'" -ForegroundColor White
Write-Host "   4. Try: 'Find me wireless headphones'" -ForegroundColor White

Write-Host "`n💡 Get your OpenAI API key:" -ForegroundColor Yellow
Write-Host "   https://platform.openai.com/api-keys" -ForegroundColor White




