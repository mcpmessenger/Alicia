# 🔧 Web Portal Troubleshooting Guide

## 🚨 **Current Issue: Network Error**

The web portal is showing "Network error" because it's trying to make API calls to `/api/configure` but there's no HTTP endpoint available.

## 🛠️ **Quick Fixes:**

### **Option 1: Local Testing (Recommended)**
1. **Download the files**:
   ```bash
   git clone https://github.com/mcpmessenger/Alicia.git
   cd Alicia
   ```

2. **Open `web-portal.html` in your browser**
3. **Modify the JavaScript** to use a mock API for testing

### **Option 2: Set up API Gateway**
1. **Create API Gateway**:
   ```bash
   aws apigateway create-rest-api \
     --name "AI Assistant Pro Web Portal" \
     --description "Web portal for API key configuration" \
     --profile ai-assistant-pro
   ```

2. **Configure the API Gateway** to connect to the Lambda function
3. **Deploy the API Gateway** to get a public URL

### **Option 3: Use Lambda Function URL (Easiest)**
1. **Create a Function URL**:
   ```bash
   aws lambda create-function-url-config \
     --function-name ai-assistant-web-portal-dev \
     --auth-type NONE \
     --profile ai-assistant-pro
   ```

2. **Get the Function URL**:
   ```bash
   aws lambda get-function-url-config \
     --function-name ai-assistant-web-portal-dev \
     --profile ai-assistant-pro
   ```

## 🎯 **Immediate Solution:**

For now, you can test the web portal by:

1. **Opening the HTML file directly** in your browser
2. **Using the Lambda function directly** to save API keys
3. **Testing the Alexa skill** with configured API keys

## 📋 **Next Steps:**

1. **Choose one of the options above**
2. **Set up the HTTP endpoint**
3. **Test the web portal**
4. **Configure API keys**
5. **Test the Alexa skill**

The web portal design is perfect - we just need to connect it to a proper HTTP endpoint! 🚀
