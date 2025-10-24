# Manual Deployment Guide - AI Assistant Pro

Due to AWS permission limitations, here's a step-by-step manual deployment guide:

## 🔧 **Step 1: Request Additional AWS Permissions**

Contact your AWS administrator to add these permissions to your user:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:*",
                "kms:*",
                "apigateway:*",
                "lambda:*",
                "s3:*",
                "iam:*"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🚀 **Step 2: Manual Resource Creation**

### **2.1 Create DynamoDB Table**
```bash
aws dynamodb create-table \
    --table-name ai-assistant-users-dev \
    --attribute-definitions AttributeName=userId,AttributeType=S \
    --key-schema AttributeName=userId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

### **2.2 Create KMS Key**
```bash
aws kms create-key \
    --description "AI Assistant Pro API Key Encryption" \
    --key-usage ENCRYPT_DECRYPT \
    --key-spec SYMMETRIC_DEFAULT
```

### **2.3 Create IAM Role for Lambda**
```bash
# Create trust policy
cat > lambda-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create role
aws iam create-role \
    --role-name ai-assistant-lambda-role-dev \
    --assume-role-policy-document file://lambda-trust-policy.json

# Attach basic execution policy
aws iam attach-role-policy \
    --role-name ai-assistant-lambda-role-dev \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

### **2.4 Create Lambda Function**
```bash
# Create deployment package
mkdir lambda-package
cp lambda_function.py lambda-package/
cp requirements.txt lambda-package/
cd lambda-package
pip install -r requirements.txt -t .
zip -r ../lambda-function.zip .
cd ..
rm -rf lambda-package

# Create Lambda function
aws lambda create-function \
    --function-name ai-assistant-alexa-skill-dev \
    --runtime python3.11 \
    --role arn:aws:iam::YOUR_ACCOUNT_ID:role/ai-assistant-lambda-role-dev \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda-function.zip \
    --timeout 30 \
    --memory-size 512
```

## 🔐 **Step 3: Configure Security**

### **3.1 Update KMS Key Policy**
```bash
# Get your account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create KMS key policy
cat > kms-key-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${ACCOUNT_ID}:root"
            },
            "Action": "kms:*",
            "Resource": "*"
        },
        {
            "Sid": "Allow Lambda to decrypt",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::${ACCOUNT_ID}:role/ai-assistant-lambda-role-dev"
            },
            "Action": [
                "kms:Decrypt",
                "kms:DescribeKey"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Update KMS key policy
aws kms put-key-policy \
    --key-id YOUR_KMS_KEY_ID \
    --policy-name default \
    --policy file://kms-key-policy.json
```

### **3.2 Add DynamoDB Permissions to Lambda Role**
```bash
# Create DynamoDB policy
cat > dynamodb-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:${ACCOUNT_ID}:table/ai-assistant-users-dev"
        }
    ]
}
EOF

# Create and attach policy
aws iam create-policy \
    --policy-name AIAssistantDynamoDBAccess \
    --policy-document file://dynamodb-policy.json

aws iam attach-role-policy \
    --role-name ai-assistant-lambda-role-dev \
    --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/AIAssistantDynamoDBAccess
```

## 🌐 **Step 4: Create API Gateway (Optional)**

```bash
# Create REST API
aws apigateway create-rest-api \
    --name ai-assistant-web-portal-dev \
    --description "API Gateway for AI Assistant Pro web portal"
```

## 📱 **Step 5: Create Alexa Skill**

1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Click "Create Skill"
3. Choose:
   - **Skill name**: AI Assistant Pro
   - **Default language**: English (US)
   - **Primary skill type**: Custom
   - **Hosting service**: AWS Lambda ARN
4. Enter your Lambda function ARN
5. Import the interaction model from `alexa-interaction-model.json`

## 🧪 **Step 6: Test the Skill**

1. Enable the skill in your Alexa app
2. Say "Alexa, open AI Assistant Pro"
3. Follow the setup instructions
4. Test with: "Ask OpenAI, what is the capital of France?"

## 💰 **Expected Costs**

- **DynamoDB**: ~$1.25/month (pay-per-request)
- **Lambda**: ~$0.50/month (1M requests)
- **KMS**: ~$1.03/month (1 key + operations)
- **API Gateway**: ~$0.35/month (100K requests)
- **Total**: ~$3.65/month

## 🔧 **Troubleshooting**

### **Common Issues:**
1. **Permission denied**: Contact AWS admin for additional permissions
2. **Lambda timeout**: Increase timeout to 30 seconds
3. **DynamoDB errors**: Check table name and permissions
4. **KMS errors**: Verify key policy and permissions

### **Debug Commands:**
```bash
# Check Lambda logs
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/ai-assistant

# Test Lambda function
aws lambda invoke \
    --function-name ai-assistant-alexa-skill-dev \
    --payload '{"test": "data"}' \
    response.json

# Check DynamoDB table
aws dynamodb describe-table --table-name ai-assistant-users-dev
```

## 📞 **Support**

If you encounter issues:
1. Check AWS CloudWatch logs
2. Verify IAM permissions
3. Test each component individually
4. Contact AWS support if needed

---

**Note**: This manual deployment requires AWS administrator privileges for some resources. Consider using AWS CloudFormation once permissions are properly configured.
