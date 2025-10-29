# Deploy Bright Mode Fix to Lambda
# This script packages and deploys the updated Lambda function with BRIGHT APL

Write-Host "🎨 Deploying BRIGHT MODE Fix to AWS Lambda..." -ForegroundColor Cyan

# Step 1: Create deployment package
Write-Host "`n📦 Step 1: Creating deployment package..." -ForegroundColor Yellow
if (Test-Path "lambda-bright-fix.zip") {
    Remove-Item "lambda-bright-fix.zip" -Force
}

Compress-Archive -Path "lambda_bright_deploy.py" -DestinationPath "lambda-bright-fix.zip" -Force

if (Test-Path "lambda-bright-fix.zip") {
    Write-Host "✅ Deployment package created: lambda-bright-fix.zip" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create deployment package" -ForegroundColor Red
    exit 1
}

# Step 2: Get Lambda function name
Write-Host "`n🔍 Step 2: Finding Lambda function..." -ForegroundColor Yellow
$functionName = Read-Host "Enter your Lambda function name (default: ai-pro-alexa-skill)"
if ([string]::IsNullOrWhiteSpace($functionName)) {
    $functionName = "ai-pro-alexa-skill"
}

Write-Host "Using function name: $functionName" -ForegroundColor Cyan

# Step 3: Update Lambda function code
Write-Host "`n🚀 Step 3: Uploading to AWS Lambda..." -ForegroundColor Yellow
try {
    aws lambda update-function-code `
        --function-name $functionName `
        --zip-file fileb://lambda-bright-fix.zip
    
    Write-Host "✅ Lambda function code updated!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to update Lambda function. Error: $_" -ForegroundColor Red
    Write-Host "`n💡 Make sure you have AWS CLI configured and proper permissions." -ForegroundColor Yellow
    exit 1
}

# Step 4: Update handler (if needed)
Write-Host "`n🔧 Step 4: Updating Lambda handler..." -ForegroundColor Yellow
try {
    aws lambda update-function-configuration `
        --function-name $functionName `
        --handler lambda_bright_deploy.lambda_handler
    
    Write-Host "✅ Lambda handler updated!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Warning: Could not update handler. You may need to update it manually in AWS Console." -ForegroundColor Yellow
}

# Step 5: Instructions
Write-Host "`n" -NoNewline
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Go to Alexa Developer Console" -ForegroundColor White
Write-Host "   2. Click 'Build' tab" -ForegroundColor White
Write-Host "   3. Click 'Save Model' button" -ForegroundColor White
Write-Host "   4. Wait for the build to complete" -ForegroundColor White
Write-Host "   5. Go to 'Test' tab and try your skill" -ForegroundColor White
Write-Host ""
Write-Host "🎨 Your Alexa device should now show the BRIGHT WHITE display!" -ForegroundColor Green
Write-Host ""
Write-Host "Test commands:" -ForegroundColor Yellow
Write-Host "   'Alexa, ask AI Pro to show me headphones'" -ForegroundColor Cyan
Write-Host "   'Alexa, ask AI Pro to find smart watches'" -ForegroundColor Cyan
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan


