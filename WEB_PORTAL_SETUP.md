# 🌐 AI Assistant Pro - Modern Web Portal Setup

## ✨ Features

- **Glassmorphism Design**: Modern, dark mode interface with thin lines and translucent elements
- **Responsive Layout**: Works perfectly on desktop and mobile devices
- **Secure API Key Storage**: Uses AWS KMS encryption for all API keys
- **Multi-Provider Support**: Configure OpenAI, Claude, and Gemini in one place
- **Real-time Feedback**: Instant success/error messages with smooth animations

## 🚀 Quick Setup

### 1. Deploy the Web Portal Lambda Function

```bash
# Create the web portal Lambda function
aws lambda create-function \
  --function-name ai-assistant-web-portal-dev \
  --runtime python3.11 \
  --role arn:aws:iam::396608803476:role/ai-assistant-lambda-role-dev \
  --handler web_portal.lambda_handler \
  --zip-file fileb://web-portal.zip \
  --environment Variables="{DYNAMODB_TABLE=ai-assistant-users-dev,KMS_KEY_ID=9ea15006-418b-417a-8d97-34015642d236}" \
  --timeout 30 \
  --memory-size 512 \
  --profile ai-assistant-pro
```

### 2. Create API Gateway (Optional)

For a public web portal, create an API Gateway:

```bash
# Create REST API
aws apigateway create-rest-api \
  --name "AI Assistant Pro Web Portal" \
  --description "Web portal for API key configuration" \
  --profile ai-assistant-pro
```

### 3. Access the Web Portal

The web portal provides a modern, glassmorphism interface for configuring API keys:

#### 🎨 Design Features:
- **Dark Mode**: Deep blue gradient background
- **Glassmorphism**: Translucent cards with backdrop blur
- **Thin Lines**: Minimal borders and clean typography
- **Smooth Animations**: Hover effects and transitions
- **Responsive**: Works on all device sizes

#### 🔧 Functionality:
- **Provider Selection**: Visual cards for OpenAI, Claude, Gemini
- **Secure Input**: Password fields for API keys
- **User ID Input**: For linking to Alexa accounts
- **Real-time Validation**: Instant feedback on form submission
- **Loading States**: Smooth loading animations

## 📱 User Experience

### For Users:
1. **Visit the web portal** (URL will be provided after API Gateway setup)
2. **Select a provider** by clicking on the provider cards
3. **Enter API key** in the secure password field
4. **Enter User ID** from their Alexa app
5. **Click Save** to securely store the configuration

### Voice Commands After Setup:
- "Alexa, open AI Assistant Pro"
- "Ask OpenAI, what is machine learning?"
- "Set Claude as my default"
- "What is artificial intelligence?" (uses default provider)

## 🔐 Security Features

- **KMS Encryption**: All API keys encrypted with AWS KMS
- **Secure Storage**: Keys stored in DynamoDB with encryption
- **User Isolation**: Each user's keys are separate
- **No Plain Text**: Keys never stored in plain text

## 🎯 Next Steps

1. **Deploy the Lambda function** (command above)
2. **Set up API Gateway** for public access
3. **Test the web portal** with sample API keys
4. **Share the URL** with users for configuration

The web portal is now ready with a beautiful, modern interface that matches your glassmorphism design requirements! 🎉
