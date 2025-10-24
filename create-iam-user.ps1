# Create New IAM User for AI Assistant Pro
# This script creates a dedicated IAM user with the necessary permissions

param(
    [string]$UserName = "ai-assistant-pro-user",
    [string]$Region = "us-east-1"
)

Write-Host "🔐 Creating IAM User for AI Assistant Pro..." -ForegroundColor Green

# Create the IAM user
Write-Host "👤 Creating IAM user: $UserName" -ForegroundColor Yellow
try {
    aws iam create-user --user-name $UserName
    Write-Host "✅ IAM user created successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create IAM user: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create access key for the user
Write-Host "🔑 Creating access key..." -ForegroundColor Yellow
try {
    $accessKey = aws iam create-access-key --user-name $UserName
    $accessKeyId = ($accessKey | ConvertFrom-Json).AccessKey.AccessKeyId
    $secretKey = ($accessKey | ConvertFrom-Json).AccessKey.SecretAccessKey
    
    Write-Host "✅ Access key created" -ForegroundColor Green
    Write-Host "🔑 Access Key ID: $accessKeyId" -ForegroundColor Cyan
    Write-Host "🔐 Secret Access Key: $secretKey" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Save these credentials securely!" -ForegroundColor Red
    Write-Host "⚠️  The secret key will not be shown again!" -ForegroundColor Red
} catch {
    Write-Host "❌ Failed to create access key: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create custom policy for AI Assistant Pro
Write-Host "📋 Creating custom policy..." -ForegroundColor Yellow
$policyDocument = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:*",
                "lambda:*",
                "kms:*",
                "apigateway:*",
                "s3:*",
                "iam:*",
                "logs:*",
                "cloudformation:*"
            ],
            "Resource": "*"
        }
    ]
}
"@

$policyDocument | Out-File -FilePath "ai-assistant-policy.json" -Encoding UTF8

try {
    aws iam create-policy `
        --policy-name AIAssistantProFullAccess `
        --policy-document file://ai-assistant-policy.json
    Write-Host "✅ Custom policy created" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create policy: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Attach the policy to the user
Write-Host "🔗 Attaching policy to user..." -ForegroundColor Yellow
try {
    $accountId = aws sts get-caller-identity --query Account --output text
    aws iam attach-user-policy `
        --user-name $UserName `
        --policy-arn "arn:aws:iam::${accountId}:policy/AIAssistantProFullAccess"
    Write-Host "✅ Policy attached successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to attach policy: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Create credentials file for the new user
Write-Host "📝 Creating AWS credentials file..." -ForegroundColor Yellow
$credentialsContent = @"
[ai-assistant-pro]
aws_access_key_id = $accessKeyId
aws_secret_access_key = $secretKey
region = $Region
"@

$credentialsContent | Out-File -FilePath "ai-assistant-credentials.txt" -Encoding UTF8

Write-Host ""
Write-Host "🎉 IAM User Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure AWS CLI with new credentials:" -ForegroundColor White
Write-Host "   aws configure --profile ai-assistant-pro" -ForegroundColor Gray
Write-Host "   # Use the Access Key ID and Secret Key shown above" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Test the new profile:" -ForegroundColor White
Write-Host "   aws sts get-caller-identity --profile ai-assistant-pro" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Deploy the infrastructure:" -ForegroundColor White
Write-Host "   aws cloudformation deploy --template-file ai-assistant-infrastructure.yaml --stack-name ai-assistant-pro --capabilities CAPABILITY_NAMED_IAM --profile ai-assistant-pro" -ForegroundColor Gray
Write-Host ""
Write-Host "🔐 Credentials saved to: ai-assistant-credentials.txt" -ForegroundColor Yellow
Write-Host "⚠️  Keep these credentials secure and never commit them to version control!" -ForegroundColor Red
