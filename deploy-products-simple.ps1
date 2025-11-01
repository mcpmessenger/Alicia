# Deploy Lambda with products-simple.json
$FUNCTION_NAME = "ai-assistant-lambda-dev"
$ZIP_FILE = "lambda-with-products.zip"

Write-Host "Deploying Lambda with 108 products..."

# Clean old zip
if (Test-Path $ZIP_FILE) {
    Remove-Item $ZIP_FILE
}

# Create zip
Set-Location "lambda-current"
Compress-Archive -Path "lambda_ai_pro_secure.py","shopping_tools.py","products-simple.json" -DestinationPath "..\$ZIP_FILE"
Set-Location ..

Write-Host "Created deployment package: $ZIP_FILE"

# Deploy to Lambda
Write-Host "Uploading to Lambda..."
aws lambda update-function-code --function-name $FUNCTION_NAME --zip-file "fileb://$ZIP_FILE"

if ($LASTEXITCODE -eq 0) {
    Write-Host "SUCCESS! Lambda updated with 108 products"
    Write-Host "Test with: 'Alexa, ask AI Pro to show me headphones'"
} else {
    Write-Host "Deployment failed. Upload $ZIP_FILE manually to Lambda console"
}


