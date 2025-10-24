# Create New IAM User for AI Assistant Pro
param(
    [string]$UserName = "ai-assistant-pro-user"
)

Write-Host "Creating IAM User for AI Assistant Pro..." -ForegroundColor Green

# Create the IAM user
Write-Host "Creating IAM user: $UserName" -ForegroundColor Yellow
aws iam create-user --user-name $UserName

# Create access key for the user
Write-Host "Creating access key..." -ForegroundColor Yellow
$accessKey = aws iam create-access-key --user-name $UserName
$accessKeyId = ($accessKey | ConvertFrom-Json).AccessKey.AccessKeyId
$secretKey = ($accessKey | ConvertFrom-Json).AccessKey.SecretAccessKey

Write-Host "Access Key ID: $accessKeyId" -ForegroundColor Cyan
Write-Host "Secret Access Key: $secretKey" -ForegroundColor Cyan
Write-Host "IMPORTANT: Save these credentials securely!" -ForegroundColor Red

# Create custom policy
Write-Host "Creating custom policy..." -ForegroundColor Yellow
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

aws iam create-policy --policy-name AIAssistantProFullAccess --policy-document file://ai-assistant-policy.json

# Attach the policy to the user
Write-Host "Attaching policy to user..." -ForegroundColor Yellow
$accountId = aws sts get-caller-identity --query Account --output text
aws iam attach-user-policy --user-name $UserName --policy-arn "arn:aws:iam::${accountId}:policy/AIAssistantProFullAccess"

# Create credentials file
$credentialsContent = @"
[ai-assistant-pro]
aws_access_key_id = $accessKeyId
aws_secret_access_key = $secretKey
region = us-east-1
"@

$credentialsContent | Out-File -FilePath "ai-assistant-credentials.txt" -Encoding UTF8

Write-Host ""
Write-Host "IAM User Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Configure AWS CLI: aws configure --profile ai-assistant-pro" -ForegroundColor White
Write-Host "2. Test: aws sts get-caller-identity --profile ai-assistant-pro" -ForegroundColor White
Write-Host "3. Deploy: aws cloudformation deploy --template-file ai-assistant-infrastructure.yaml --stack-name ai-assistant-pro --capabilities CAPABILITY_NAMED_IAM --profile ai-assistant-pro" -ForegroundColor White
