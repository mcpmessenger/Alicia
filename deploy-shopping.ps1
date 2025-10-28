# deploy-shopping.ps1
# Deployment script for AI Pro Shopping Assistant

param(
    [string]$AmazonAssociatesId = "ai-pro-20",
    [string]$ShareASaleId = "",
    [string]$CJAffiliateId = "",
    [string]$OpenAIAPIKey = "",
    [string]$GeminiAPIKey = "",
    [string]$ClaudeAPIKey = "",
    [string]$DynamoDBTable = "ai-assistant-users-dev",
    [string]$AWSRegion = "us-east-1"
)

Write-Host "🚀 Deploying AI Pro Shopping Assistant..." -ForegroundColor Cyan

# Check if AWS CLI is installed
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI not found. Please install AWS CLI first." -ForegroundColor Red
    exit 1
}

# Check if user is logged in to AWS
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "✅ AWS CLI authenticated" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI not authenticated. Please run 'aws configure' first." -ForegroundColor Red
    exit 1
}

# Create deployment package for main Lambda function
Write-Host "📦 Creating deployment package for main Lambda function..." -ForegroundColor Yellow

$lambdaFiles = @(
    "lambda_ai_pro_shopping.py",
    "shopping_tools.py"
)

# Create temporary directory for packaging
$tempDir = "lambda-package-shopping"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copy files to temp directory
foreach ($file in $lambdaFiles) {
    if (Test-Path $file) {
        Copy-Item $file $tempDir
        Write-Host "  ✅ Copied $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ File not found: $file" -ForegroundColor Red
    }
}

# Rename main file to lambda_function.py
if (Test-Path "$tempDir/lambda_ai_pro_shopping.py") {
    Rename-Item "$tempDir/lambda_ai_pro_shopping.py" "$tempDir/lambda_function.py"
}

# Create zip file
$zipFile = "lambda-shopping-deployment.zip"
if (Test-Path $zipFile) {
    Remove-Item $zipFile
}

Compress-Archive -Path "$tempDir/*" -DestinationPath $zipFile
Write-Host "  ✅ Created $zipFile" -ForegroundColor Green

# Clean up temp directory
Remove-Item $tempDir -Recurse -Force

# Create deployment package for web portal
Write-Host "📦 Creating deployment package for web portal..." -ForegroundColor Yellow

$webPortalFiles = @(
    "web_portal_shopping.py",
    "web-portal-shopping.html"
)

$webTempDir = "web-portal-package"
if (Test-Path $webTempDir) {
    Remove-Item $webTempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $webTempDir | Out-Null

foreach ($file in $webPortalFiles) {
    if (Test-Path $file) {
        Copy-Item $file $webTempDir
        Write-Host "  ✅ Copied $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ File not found: $file" -ForegroundColor Red
    }
}

# Rename main file to lambda_function.py
if (Test-Path "$webTempDir/web_portal_shopping.py") {
    Rename-Item "$webTempDir/web_portal_shopping.py" "$webTempDir/lambda_function.py"
}

# Create zip file for web portal
$webZipFile = "web-portal-shopping-deployment.zip"
if (Test-Path $webZipFile) {
    Remove-Item $webZipFile
}

Compress-Archive -Path "$webTempDir/*" -DestinationPath $webZipFile
Write-Host "  ✅ Created $webZipFile" -ForegroundColor Green

# Clean up temp directory
Remove-Item $webTempDir -Recurse -Force

# Deploy main Lambda function
Write-Host "🚀 Deploying main Lambda function..." -ForegroundColor Yellow

try {
    aws lambda update-function-code `
        --function-name ai-pro-alexa-skill `
        --zip-file "fileb://$zipFile" `
        --region $AWSRegion

    Write-Host "  ✅ Main Lambda function updated" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed to update main Lambda function: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Update environment variables for main Lambda function
Write-Host "🔧 Updating environment variables..." -ForegroundColor Yellow

$envVars = @{
    "AMAZON_ASSOCIATES_ID" = $AmazonAssociatesId
    "DYNAMODB_TABLE" = $DynamoDBTable
    "AWS_REGION" = $AWSRegion
}

if ($ShareASaleId) {
    $envVars["SHAREASALE_ID"] = $ShareASaleId
}

if ($CJAffiliateId) {
    $envVars["CJ_AFFILIATE_ID"] = $CJAffiliateId
}

if ($OpenAIAPIKey) {
    $envVars["OPENAI_API_KEY"] = $OpenAIAPIKey
}

if ($GeminiAPIKey) {
    $envVars["GEMINI_API_KEY"] = $GeminiAPIKey
}

if ($ClaudeAPIKey) {
    $envVars["CLAUDE_API_KEY"] = $ClaudeAPIKey
}

# Convert to JSON format for AWS CLI
$envJson = $envVars | ConvertTo-Json -Compress

try {
    aws lambda update-function-configuration `
        --function-name ai-pro-alexa-skill `
        --environment Variables=$envJson `
        --region $AWSRegion

    Write-Host "  ✅ Environment variables updated" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed to update environment variables: $($_.Exception.Message)" -ForegroundColor Red
}

# Deploy web portal Lambda function
Write-Host "🌐 Deploying web portal Lambda function..." -ForegroundColor Yellow

try {
    aws lambda update-function-code `
        --function-name ai-assistant-web-portal-dev `
        --zip-file "fileb://$webZipFile" `
        --region $AWSRegion

    Write-Host "  ✅ Web portal Lambda function updated" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed to update web portal Lambda function: $($_.Exception.Message)" -ForegroundColor Red
}

# Update web portal environment variables
try {
    aws lambda update-function-configuration `
        --function-name ai-assistant-web-portal-dev `
        --environment Variables=$envJson `
        --region $AWSRegion

    Write-Host "  ✅ Web portal environment variables updated" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed to update web portal environment variables: $($_.Exception.Message)" -ForegroundColor Red
}

# Clean up deployment files
Write-Host "🧹 Cleaning up deployment files..." -ForegroundColor Yellow
Remove-Item $zipFile -ErrorAction SilentlyContinue
Remove-Item $webZipFile -ErrorAction SilentlyContinue

Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Update your Alexa skill endpoint to use the new Lambda function" -ForegroundColor White
Write-Host "2. Import the updated interaction model (alexa-interaction-model.json)" -ForegroundColor White
Write-Host "3. Test the shopping functionality with voice commands" -ForegroundColor White
Write-Host "4. Access the web portal to configure API keys and test shopping" -ForegroundColor White
Write-Host ""
Write-Host "🎤 Voice Commands to Test:" -ForegroundColor Cyan
Write-Host "• 'Alexa, open AI Pro'" -ForegroundColor White
Write-Host "• 'Find me noise-canceling headphones under 200 dollars'" -ForegroundColor White
Write-Host "• 'Search for the best coffee maker'" -ForegroundColor White
Write-Host "• 'Show me electronics laptops'" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Web Portal:" -ForegroundColor Cyan
Write-Host "• Access the web portal to configure API keys" -ForegroundColor White
Write-Host "• Test product searches with visual results" -ForegroundColor White
Write-Host "• View affiliate links and product details" -ForegroundColor White
