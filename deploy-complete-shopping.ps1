# deploy-complete-shopping.ps1
# Complete Shopping Assistant Deployment Script

Write-Host "AI Pro Complete Shopping Assistant - Deployment" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$FUNCTION_NAME = "ai-pro-alexa-skill"
$REGION = "us-east-1"
$DYNAMODB_TABLE = "ai-assistant-users-dev"

Write-Host "[Step 1] Packaging Lambda function..." -ForegroundColor Yellow

# Create temporary directory for packaging
$tempDir = "temp_lambda_package"
if (Test-Path $tempDir) {
    Remove-Item -Path $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy Lambda files
Copy-Item "lambda_ai_pro_complete_shopping.py" "$tempDir/lambda_function.py"
Copy-Item "shopping_tools.py" "$tempDir/"

# Create ZIP file
$zipFile = "lambda-complete-shopping-deployment.zip"
if (Test-Path $zipFile) {
    Remove-Item $zipFile -Force
}

Write-Host "Creating ZIP archive..." -ForegroundColor Gray
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipFile -Force

# Cleanup temp directory
Remove-Item -Path $tempDir -Recurse -Force

Write-Host "[OK] Package created: $zipFile" -ForegroundColor Green
Write-Host ""

# Ask for affiliate ID
Write-Host "[Step 2] Configure Affiliate Settings" -ForegroundColor Yellow
$affiliateId = Read-Host "Enter your Amazon Associates ID (e.g., yourname-20) [Press Enter to skip]"

if ([string]::IsNullOrWhiteSpace($affiliateId)) {
    $affiliateId = "ai-pro-20"
    Write-Host "Using default affiliate ID: $affiliateId" -ForegroundColor Gray
}

Write-Host ""
Write-Host "[Step 3] Deploying to AWS Lambda..." -ForegroundColor Yellow

try {
    # Update Lambda function code
    Write-Host "Uploading function code..." -ForegroundColor Gray
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://$zipFile `
        --region $REGION
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Function code updated successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Error updating function code" -ForegroundColor Red
        exit 1
    }
    
    # Wait for update to complete
    Write-Host "Waiting for deployment to complete..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    # Update environment variables
    Write-Host "Configuring environment variables..." -ForegroundColor Gray
    
    # AWS CLI format: Variables={Key1=Value1,Key2=Value2}
    $envVars = "Variables={AMAZON_ASSOCIATES_ID=$affiliateId,DYNAMODB_TABLE=$DYNAMODB_TABLE}"
    
    aws lambda update-function-configuration `
        --function-name $FUNCTION_NAME `
        --environment $envVars `
        --region $REGION
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Environment variables configured" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Error configuring environment variables" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "[ERROR] Deployment error: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Deployment Complete!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Update Alexa Interaction Model:" -ForegroundColor White
Write-Host "   - Go to: https://developer.amazon.com/alexa/console/ask" -ForegroundColor Gray
Write-Host "   - Select your skill -> Build -> JSON Editor" -ForegroundColor Gray
Write-Host "   - Copy contents from: alexa-interaction-model-complete.json" -ForegroundColor Gray
Write-Host "   - Paste and click 'Build Model'" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Enable APL Interface:" -ForegroundColor White
Write-Host "   - Go to: Interfaces tab" -ForegroundColor Gray
Write-Host "   - Enable 'Alexa Presentation Language'" -ForegroundColor Gray
Write-Host "   - Save Interfaces" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Test Your Skill:" -ForegroundColor White
Write-Host "   - Go to Test tab" -ForegroundColor Gray
Write-Host "   - Try: 'ask AI Pro to find me headphones'" -ForegroundColor Gray
Write-Host "   - Then: 'add item 1'" -ForegroundColor Gray
Write-Host "   - Then: 'view cart'" -ForegroundColor Gray
Write-Host "   - Then: 'checkout now'" -ForegroundColor Gray
Write-Host "   - Then: 'yes, buy it'" -ForegroundColor Gray
Write-Host ""

Write-Host "DOCUMENTATION:" -ForegroundColor Yellow
Write-Host "   - Complete guide: COMPLETE_SHOPPING_GUIDE.md" -ForegroundColor Gray
Write-Host "   - Visual flow: SHOPPING_FLOW_DIAGRAM.md" -ForegroundColor Gray
Write-Host ""

Write-Host "MONETIZATION:" -ForegroundColor Yellow
Write-Host "   - Affiliate ID: $affiliateId" -ForegroundColor Gray
Write-Host "   - Sign up: https://affiliate-program.amazon.com/" -ForegroundColor Gray
Write-Host ""

Write-Host "Happy Shopping!" -ForegroundColor Green

