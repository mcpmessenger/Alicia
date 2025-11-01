# Deploy Lambda with all 108 products from products-simple.json
# This updates your Alexa skill to use the complete product catalog

Write-Host "🚀 Deploying Lambda with 108 products..." -ForegroundColor Cyan

# Configuration
$LAMBDA_FUNCTION_NAME = "ai-assistant-lambda-dev"  # Change if different
$ZIP_FILE = "lambda-with-products.zip"

# Step 1: Clean up old zip if exists
if (Test-Path $ZIP_FILE) {
    Remove-Item $ZIP_FILE -Force
    Write-Host "✅ Cleaned up old deployment package" -ForegroundColor Green
}

# Step 2: Create deployment package
Write-Host "`n📦 Creating deployment package..." -ForegroundColor Yellow
Set-Location "lambda-current"

# Create zip with all required files
Compress-Archive -Path @(
    "lambda_ai_pro_secure.py",
    "shopping_tools.py",
    "products-simple.json"
) -DestinationPath "..\$ZIP_FILE" -Force

Set-Location ..

if (Test-Path $ZIP_FILE) {
    $zipSize = (Get-Item $ZIP_FILE).Length / 1MB
    Write-Host "✅ Created $ZIP_FILE ($([math]::Round($zipSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to create deployment package" -ForegroundColor Red
    exit 1
}

# Step 3: Check AWS CLI
Write-Host "`n🔍 Checking AWS CLI..." -ForegroundColor Yellow
try {
    $awsVersion = aws --version 2>&1
    Write-Host "✅ AWS CLI found: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not found. Please install: https://aws.amazon.com/cli/" -ForegroundColor Red
    Write-Host "Or upload $ZIP_FILE manually to Lambda console" -ForegroundColor Yellow
    exit 1
}

# Step 4: Deploy to Lambda
Write-Host "`n☁️  Deploying to AWS Lambda..." -ForegroundColor Yellow
Write-Host "Function: $LAMBDA_FUNCTION_NAME" -ForegroundColor Cyan

try {
    $result = aws lambda update-function-code `
        --function-name $LAMBDA_FUNCTION_NAME `
        --zip-file "fileb://$ZIP_FILE" `
        2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Lambda function updated successfully!" -ForegroundColor Green
        
        # Wait a moment for function to update
        Write-Host "`n⏳ Waiting for function to update..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        
        # Get function info
        $funcInfo = aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME | ConvertFrom-Json
        $codeSize = [math]::Round($funcInfo.Configuration.CodeSize / 1MB, 2)
        
        Write-Host "✅ Function updated:" -ForegroundColor Green
        Write-Host "   - Runtime: $($funcInfo.Configuration.Runtime)" -ForegroundColor White
        Write-Host "   - Code Size: $codeSize MB" -ForegroundColor White
        Write-Host "   - Last Modified: $($funcInfo.Configuration.LastModified)" -ForegroundColor White
        
    } else {
        Write-Host "❌ Deployment failed!" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error deploying to Lambda: $_" -ForegroundColor Red
    Write-Host "`n💡 You can upload manually:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://console.aws.amazon.com/lambda/" -ForegroundColor White
    Write-Host "   2. Find function: $LAMBDA_FUNCTION_NAME" -ForegroundColor White
    Write-Host "   3. Click 'Upload from' → '.zip file'" -ForegroundColor White
    Write-Host "   4. Upload: $ZIP_FILE" -ForegroundColor White
    exit 1
}

# Step 5: Test the function
Write-Host "`n🧪 Testing Lambda function..." -ForegroundColor Yellow

$testEvent = @{
    "version" = "1.0"
    "session" = @{
        "new" = $true
        "sessionId" = "test-session-$(Get-Random)"
        "user" = @{
            "userId" = "test-user"
        }
    }
    "request" = @{
        "type" = "IntentRequest"
        "intent" = @{
            "name" = "SearchProductIntent"
            "slots" = @{
                "product" = @{
                    "value" = "headphones"
                }
            }
        }
    }
} | ConvertTo-Json -Depth 10

$testEventFile = "test-deployment.json"
$testEvent | Out-File -FilePath $testEventFile -Encoding UTF8

try {
    Write-Host "Invoking Lambda with test query: 'headphones'..." -ForegroundColor Cyan
    
    $invokeResult = aws lambda invoke `
        --function-name $LAMBDA_FUNCTION_NAME `
        --payload file://$testEventFile `
        --cli-binary-format raw-in-base64-out `
        response.json `
        2>&1
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path "response.json")) {
        $response = Get-Content "response.json" | ConvertFrom-Json
        
        if ($response.response.outputSpeech.ssml) {
            Write-Host "✅ Lambda test successful!" -ForegroundColor Green
            Write-Host "Response: $($response.response.outputSpeech.ssml)" -ForegroundColor White
        } else {
            Write-Host "⚠️  Lambda executed but response format unexpected" -ForegroundColor Yellow
            Write-Host (Get-Content "response.json") -ForegroundColor Gray
        }
        
        # Clean up test files
        Remove-Item $testEventFile -ErrorAction SilentlyContinue
        Remove-Item "response.json" -ErrorAction SilentlyContinue
    } else {
        Write-Host "⚠️  Lambda invoke failed" -ForegroundColor Yellow
        Write-Host $invokeResult -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️  Could not test Lambda: $_" -ForegroundColor Yellow
}

# Done!
Write-Host "`n✅ DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "`n📱 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open Alexa Developer Console" -ForegroundColor White
Write-Host "2. Test your skill with: 'ask AI Pro to show me headphones'" -ForegroundColor White
Write-Host "3. Your Alexa device should now display all 108 products!" -ForegroundColor White
Write-Host "`n💡 The APL display should now show products properly" -ForegroundColor Yellow


