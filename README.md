# AI Assistant Pro - Multi-Provider LLM Alexa Skill

A secure Alexa Skill that allows users to interact with multiple Large Language Model providers (OpenAI, Google Gemini, Anthropic Claude) using their own API keys.

## 🚨 CURRENT STATUS: APL Dark Display Bug

**Issue**: APL (Alexa Presentation Language) displays are showing completely black backgrounds instead of bright white backgrounds.

**Status**: 🔍 **INVESTIGATION IN PROGRESS** - Need community help with APL caching issues

**Key Files**:
- `APL_DARK_DISPLAY_DIAGNOSIS.md` - Complete diagnosis and research guide
- `alexa-apl-document.json` - Main APL template (modified for bright mode)
- `lambda_ai_pro_secure.py` - Lambda function with APL fixes

**Research Needed**: APL caching mechanisms, background property syntax, device-specific APL behavior

## 🚀 Features

- **Multi-Provider Support**: OpenAI GPT, Google Gemini, Anthropic Claude
- **Secure API Key Storage**: Encrypted using AWS KMS
- **Voice Commands**: Natural language interaction with AI models
- **Session Management**: Maintains conversation context
- **Web Portal**: Secure API key configuration interface
- **Shopping Assistant**: Product search and cart management (with APL display issues)

## 📋 Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.11+
- Alexa Developer Account
- API keys for desired LLM providers

## 🛠️ Installation

### 1. Deploy AWS Infrastructure

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

This will create:
- DynamoDB table for user data
- KMS key for API key encryption
- Lambda functions for Alexa Skill and web portal
- API Gateway for web portal
- S3 bucket for static assets

### 2. Configure Alexa Skill

1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Create a new skill:
   - **Skill name**: AI Assistant Pro
   - **Default language**: English (US)
   - **Primary skill type**: Custom
   - **Hosting service**: AWS Lambda ARN
3. Use the Lambda function ARN from the deployment output
4. Import the interaction model from `alexa-interaction-model.json`

### 3. Set Up API Keys

1. Access the web portal (URL provided in deployment output)
2. Enter your API keys for desired providers:
   - **OpenAI**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Anthropic**: Get from [Anthropic Console](https://console.anthropic.com/)
   - **Google**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)

## 🎤 Usage

### Voice Commands

- **Ask a question**: "Ask OpenAI, what is the capital of France?"
- **Set default provider**: "Set Claude as my default"
- **Use default provider**: "What is machine learning?"
- **Clear context**: "Start a new conversation"
- **Get help**: "Help"

### Supported Providers

| Provider | Models | API Key Format |
|----------|--------|----------------|
| OpenAI | GPT-4o, GPT-4, GPT-3.5-turbo | `sk-...` |
| Anthropic | Claude 3.5 Sonnet, Claude 3 Opus | `sk-ant-...` |
| Google | Gemini 2.0 Flash, Gemini 2.5 Pro | `AI...` |

## 🔒 Security Features

- **KMS Encryption**: All API keys encrypted at rest
- **Least Privilege**: Minimal IAM permissions
- **Secure Transmission**: Keys never logged or transmitted
- **Token-Based Auth**: Secure web portal authentication
- **Input Sanitization**: Protection against prompt injection

## 📁 Project Structure

```
├── ai-assistant-infrastructure.yaml  # CloudFormation template
├── lambda_function.py                # Main Alexa Skill handler
├── web_portal.py                    # API key configuration portal
├── alexa-interaction-model.json      # Alexa skill interaction model
├── requirements.txt                  # Python dependencies
├── deploy.sh                         # Deployment script
└── README.md                         # This file
```

## 🔧 Configuration

### Environment Variables

The Lambda functions use these environment variables:
- `DYNAMODB_TABLE`: DynamoDB table name
- `KMS_KEY_ID`: KMS key ID for encryption

### Customization

You can modify the following in `lambda_function.py`:
- Response length limits
- Model selection per provider
- Error handling messages
- Session context management

## 🧪 Testing

### Local Testing

```bash
# Test Lambda function locally
python lambda_function.py

# Test web portal
python web_portal.py
```

### Alexa Testing

1. Enable the skill in your Alexa app
2. Say "Alexa, open AI Assistant Pro"
3. Follow the setup instructions
4. Test with various voice commands

## 📊 Monitoring

Monitor your skill using:
- **CloudWatch Logs**: Lambda function logs
- **DynamoDB Metrics**: User data and API key storage
- **KMS Metrics**: Encryption/decryption operations

## 🚨 Troubleshooting

### Common Issues

1. **"API key not linked"**: Configure your API keys in the web portal
2. **"Provider not supported"**: Check provider name spelling
3. **"Error processing request"**: Check CloudWatch logs for details

### Debug Steps

1. Check CloudWatch logs for Lambda functions
2. Verify DynamoDB table has user data
3. Confirm KMS key permissions
4. Test API keys manually

## 🔄 Updates

To update the skill:

```bash
# Redeploy infrastructure
./deploy.sh

# Update Lambda function code
aws lambda update-function-code \
    --function-name ai-assistant-alexa-skill-dev \
    --zip-file fileb://lambda_function.zip
```

## 📈 Future Enhancements

- Cost tracking and reporting
- Model selection within providers
- Custom system prompts
- Multi-language support
- Advanced session management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review CloudWatch logs
- Contact the development team

---

**Note**: This skill requires users to provide their own API keys for LLM providers. Users are responsible for their own usage costs and API key security.
