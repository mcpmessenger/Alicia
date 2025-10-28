# Shopping Environment Variables Configuration

## Required Environment Variables for AI Pro Shopping Assistant

### Amazon Associates Configuration
```bash
# Amazon Associates Tracking ID (required for monetization)
AMAZON_ASSOCIATES_ID=ai-pro-20

# Optional: Additional affiliate network IDs
SHAREASALE_ID=your-shareasale-id
CJ_AFFILIATE_ID=your-cj-affiliate-id
```

### DynamoDB Configuration
```bash
# DynamoDB table name for user data and shopping results
DYNAMODB_TABLE=ai-assistant-users-dev

# AWS Region
AWS_REGION=us-east-1
```

### API Keys (Existing)
```bash
# LLM Provider API Keys
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
CLAUDE_API_KEY=your-claude-api-key
```

## How to Set Environment Variables

### 1. AWS Lambda Console
1. Go to AWS Lambda Console
2. Select your Lambda function
3. Go to Configuration → Environment variables
4. Add each variable with its value

### 2. AWS CLI
```bash
aws lambda update-function-configuration \
  --function-name ai-pro-alexa-skill \
  --environment Variables='{
    "AMAZON_ASSOCIATES_ID":"ai-pro-20",
    "SHAREASALE_ID":"your-shareasale-id",
    "CJ_AFFILIATE_ID":"your-cj-affiliate-id",
    "DYNAMODB_TABLE":"ai-assistant-users-dev",
    "AWS_REGION":"us-east-1",
    "OPENAI_API_KEY":"your-openai-api-key",
    "GEMINI_API_KEY":"your-gemini-api-key",
    "CLAUDE_API_KEY":"your-claude-api-key"
  }'
```

### 3. CloudFormation Template
Add to your `ai-assistant-infrastructure.yaml`:
```yaml
Environment:
  Variables:
    AMAZON_ASSOCIATES_ID: !Ref AmazonAssociatesId
    SHAREASALE_ID: !Ref ShareASaleId
    CJ_AFFILIATE_ID: !Ref CJAffiliateId
    DYNAMODB_TABLE: !Ref DynamoDBTable
    AWS_REGION: !Ref AWS::Region
    OPENAI_API_KEY: !Ref OpenAIAPIKey
    GEMINI_API_KEY: !Ref GeminiAPIKey
    CLAUDE_API_KEY: !Ref ClaudeAPIKey
```

## Amazon Associates Setup

### 1. Register for Amazon Associates
1. Go to [affiliate-program.amazon.com](https://affiliate-program.amazon.com)
2. Sign up for the Amazon Associates program
3. Complete the application process
4. Get your tracking ID (format: `yourname-20`)

### 2. Configure Tracking ID
- Set `AMAZON_ASSOCIATES_ID` to your tracking ID
- This will be automatically appended to all Amazon product URLs
- Example: `https://amazon.com/product?tag=ai-pro-20`

## Additional Affiliate Networks

### ShareASale
- Register at [shareasale.com](https://shareasale.com)
- Get your affiliate ID
- Set `SHAREASALE_ID` environment variable

### Commission Junction (CJ Affiliate)
- Register at [cj.com](https://cj.com)
- Get your affiliate ID
- Set `CJ_AFFILIATE_ID` environment variable

## Security Notes

- Never commit API keys or affiliate IDs to version control
- Use AWS Secrets Manager for production deployments
- Rotate API keys regularly
- Monitor affiliate link performance

## Testing

### Test Affiliate Links
1. Search for a product using the skill
2. Check the generated URLs in the response
3. Verify affiliate IDs are properly appended
4. Test click-through rates

### Monitor Performance
- Check Amazon Associates dashboard for clicks and conversions
- Monitor DynamoDB for shopping query patterns
- Review CloudWatch logs for errors

## Troubleshooting

### Common Issues
1. **Affiliate links not working**: Check `AMAZON_ASSOCIATES_ID` is set correctly
2. **No products found**: Verify API keys are valid
3. **Permission errors**: Ensure Lambda has DynamoDB access
4. **Rate limiting**: Check API usage limits

### Debug Commands
```bash
# Check environment variables
aws lambda get-function-configuration --function-name ai-pro-alexa-skill

# Test affiliate link generation
aws lambda invoke --function-name ai-pro-alexa-skill --payload '{"query":"test product"}' response.json
```
