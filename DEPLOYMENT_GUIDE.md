# 🚀 AI Pro Alexa Skill - Deployment Guide

## 📋 **Quick Start (Hardcoded Keys for Testing)**

### **Step 1: Deploy Lambda Function with Hardcoded Keys**

1. **Edit `lambda_ai_pro_fixed.py`** and replace the API key section with:
```python
# Hardcoded API keys for testing
openai_api_key = "YOUR_OPENAI_API_KEY_HERE"
gemini_api_key = "YOUR_GEMINI_API_KEY_HERE"
claude_api_key = "YOUR_CLAUDE_API_KEY_HERE"
```

2. **Deploy to AWS:**
```bash
# Package the function
Compress-Archive -Path lambda_ai_pro_fixed.py -DestinationPath lambda-deployment.zip -Force

# Update Lambda function
aws lambda update-function-code --function-name ai-pro-alexa-skill --zip-file fileb://lambda-deployment.zip

# Update handler
aws lambda update-function-configuration --function-name ai-pro-alexa-skill --handler lambda_ai_pro_fixed.lambda_handler
```

### **Step 2: Configure Alexa Skill**

1. **Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)**
2. **Select your "AI Pro" skill**
3. **Go to Build tab**
4. **Update Interaction Model** with `alexa-interaction-model.json`
5. **Go to Test tab**
6. **Test the skill:**
   - "Alexa, ask AI Pro tell me about lizards"
   - "Alexa, ask AI Pro ask Gemini tell me about space"
   - "Alexa, ask AI Pro ask Claude explain quantum computing"

## 🔐 **Production Deployment (Secure)**

### **Step 1: Set Environment Variables**

```bash
aws lambda update-function-configuration \
  --function-name ai-pro-alexa-skill \
  --environment Variables='{
    "OPENAI_API_KEY":"your-openai-key",
    "GEMINI_API_KEY":"your-gemini-key", 
    "CLAUDE_API_KEY":"your-claude-key",
    "DYNAMODB_TABLE":"ai-assistant-users-dev",
    "KMS_KEY_ID":"your-kms-key-id"
  }'
```

### **Step 2: Deploy Secure Version**

Use `lambda_ai_pro_secure.py` (no hardcoded keys) for production.

## 🎯 **Features**

- ✅ **Multi-Provider Support**: OpenAI, Gemini, Claude
- ✅ **Voice-Optimized Responses**: 2-3 sentences, conversational
- ✅ **APL Visual Interface**: Logo and branding on display devices
- ✅ **Zero Dependencies**: Uses only built-in Python libraries
- ✅ **Comprehensive Logging**: Full debugging support
- ✅ **Error Handling**: Graceful fallbacks and user feedback

## 📱 **Supported Devices**

- **Echo Show** (2nd Gen & 3rd Gen) - Full visual interface
- **Echo Spot** - Compact display
- **Alexa App** - Mobile interface
- **Echo Dot** - Voice only
- **Fire TV** - TV display

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"API key not configured"**
   - Check if keys are hardcoded or in environment variables
   - Verify DynamoDB permissions if using database lookup

2. **"There was a problem with the requested skill's response"**
   - Check CloudWatch logs for errors
   - Verify Lambda function is deployed correctly

3. **Skill not responding to wake words**
   - Check interaction model is built and deployed
   - Verify invocation name is correct ("AI Pro")

### **Debug Commands:**

```bash
# Check Lambda function status
aws lambda get-function --function-name ai-pro-alexa-skill

# View recent logs
aws logs describe-log-streams --log-group-name /aws/lambda/ai-pro-alexa-skill --order-by LastEventTime --descending --max-items 1

# Test function directly
aws lambda invoke --function-name ai-pro-alexa-skill --payload '{"test":"data"}' response.json
```

## 📊 **Monitoring**

- **CloudWatch Logs**: `/aws/lambda/ai-pro-alexa-skill`
- **Lambda Metrics**: Invocations, errors, duration
- **Alexa Analytics**: Usage, user engagement

## 🎉 **Success!**

Your AI Pro Alexa skill is now ready with:
- Multi-provider AI support
- Voice-optimized responses
- Visual interface for display devices
- Comprehensive error handling
- Production-ready security

**Test it out and enjoy your AI assistant!** 🚀
