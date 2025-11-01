# 🎉 AI Pro - Friendly Chat Assistant Setup Guide

## Overview

Your Alexa skill has been transformed from a **shopping-focused assistant** into a **friendly AI research assistant** that can discuss any topic using Gemini, OpenAI, or Anthropic! Shopping capabilities are still available but are now subtle and secondary.

---

## ✨ What Changed

### Before:
- **Primary Focus**: Shopping assistant
- **Welcome Message**: "Welcome to Al Pro Shopping! I can help you find products..."
- **Default Behavior**: Everything routed to shopping
- **Personality**: Transaction-focused

### After:
- **Primary Focus**: Friendly AI chat & research assistant
- **Welcome Messages**: Casual & inviting (e.g., "Hey! I'm AI Pro. I love chatting about anything - science, history, tech, you name it!")
- **Default Behavior**: General conversation and knowledge
- **Personality**: Curious, enthusiastic, helpful companion
- **Shopping**: Only when explicitly requested (e.g., "find me headphones")

---

## 🚀 Deployment

### Step 1: Deploy the New Lambda Function

Run the deployment script:

```powershell
.\deploy-friendly-chat.ps1
```

This will:
1. Package `lambda_ai_pro_friendly_chat.py` as your main handler
2. Include shopping_tools.py for optional shopping features
3. Upload to your existing Lambda function
4. Create a deployment package

### Step 2: Configure API Keys

You need API keys from at least ONE provider (ideally all three for best experience):

#### Get API Keys:

1. **OpenAI** (GPT-4, GPT-3.5): https://platform.openai.com/api-keys
2. **Anthropic** (Claude): https://console.anthropic.com/
3. **Google Gemini**: https://makersuite.google.com/app/apikey

#### Set Environment Variables in Lambda:

```bash
aws lambda update-function-configuration \
  --function-name ai-pro-skill \
  --environment Variables='{
    "OPENAI_API_KEY":"sk-your-openai-key-here",
    "ANTHROPIC_API_KEY":"sk-ant-your-anthropic-key",
    "GOOGLE_API_KEY":"your-google-gemini-key",
    "DYNAMODB_TABLE":"ai-assistant-users-dev"
  }' \
  --region us-east-1
```

Or set them in the AWS Console:
1. Go to AWS Lambda → Functions → `ai-pro-skill`
2. Configuration → Environment variables
3. Add the keys above

---

## 🎯 How to Use

### General Chat & Research (Primary Feature)

Users can ask ANYTHING:

**Science & Technology:**
- "Alexa, open AI Pro"
- "Tell me about quantum entanglement"
- "How do neural networks work?"
- "What's the latest in fusion energy?"

**History & Culture:**
- "What happened during the Renaissance?"
- "Tell me about ancient Egypt"
- "Who was Ada Lovelace?"

**Current Topics:**
- "Explain blockchain technology"
- "What are LLMs?"
- "Tell me about Mars missions"

**Fun & Trivia:**
- "Tell me an interesting fact"
- "What's the tallest mountain on Earth?"
- "Explain why the sky is blue"

### Choosing AI Providers

Users can explicitly choose which AI to use:

**Use Gemini:**
- "Use Gemini to explain black holes"
- "Ask Gemini about ancient Rome"
- "Gemini, what is quantum computing?"

**Use Claude (Anthropic):**
- "Use Claude to tell me about philosophy"
- "Ask Claude about machine learning"
- "Claude, explain photosynthesis"

**Use OpenAI (GPT):**
- "Use OpenAI to write a poem"
- "Ask GPT about history"
- "OpenAI, what is AI?"

**Set a Default:**
- "Set Gemini as my default"
- "Make Claude my default"
- "Use OpenAI by default"

### Shopping (Secondary Feature)

Shopping only activates with **explicit shopping intent**:

**Trigger Shopping:**
- "Find me wireless headphones"
- "Show me laptops"
- "I want to buy running shoes"
- "Search for coffee makers"

**Browse & Add to Cart:**
- (After search) "Add item 1"
- "View my cart"
- "What's in my cart?"

---

## 🧪 Testing

### Test in Alexa Developer Console

1. Go to [Alexa Developer Console](https://developer.amazon.com/alexa/console/ask)
2. Open your "AI Pro" skill
3. Click **Test** tab
4. Enable testing: "Development"

### Test Queries:

```
Alexa, open AI Pro
> "Hey! I'm AI Pro. I love chatting about anything..."

Tell me about black holes
> [Detailed, conversational explanation]

Use Gemini to explain quantum physics
> [Gemini-powered explanation]

Find me wireless headphones
> [Shows product search results with shopping UI]
```

---

## 📊 Comparison: Before vs After

| Feature | Before (Shopping Focus) | After (Chat Focus) |
|---------|------------------------|-------------------|
| **Launch Message** | "Welcome to AI Pro Shopping!" | "Hey! I'm AI Pro. Ask me anything!" |
| **Primary Use Case** | Product search | General conversation & research |
| **AI Integration** | None | OpenAI, Claude, Gemini |
| **Shopping** | Always active | Only when explicitly requested |
| **Personality** | Transactional | Friendly, curious, helpful |
| **Response to "tell me a poem"** | "Your cart is empty..." | [Actual poem response] |

---

## 🔧 Customization

### Change Welcome Messages

Edit `lambda_ai_pro_friendly_chat.py`:

```python
WELCOME_MESSAGES = [
    "Your custom welcome message here!",
    "Another friendly greeting!",
    # Add as many as you like
]
```

### Adjust AI Response Length

In each AI function (`call_openai`, `call_anthropic`, `call_gemini`):

```python
"max_tokens": 200,  # Change this (150-500 recommended for voice)
"temperature": 0.8   # Creativity (0.7-0.9 for friendly chat)
```

### Modify Shopping Detection

Edit the `SHOPPING_KEYWORDS` list to be more or less sensitive:

```python
SHOPPING_KEYWORDS = [
    'buy', 'purchase', 'shop', 'find product',
    # Add or remove keywords
]
```

---

## 🎨 Interaction Model

Your current interaction model in `alexa-interaction-model.json` should work as-is! The `LLMQueryIntent` handles both chat and shopping based on context.

If you want to emphasize chat over shopping, consider:

1. Adding more conversational sample utterances
2. Creating dedicated research/question intents
3. Moving shopping to a separate, explicit intent

---

## 💡 Pro Tips

### For Best User Experience:

1. **Configure All 3 Providers**: Users love choice!
2. **Monitor Costs**: AI API calls have costs - set usage limits
3. **Test Voice Responses**: Some AI responses are long - optimize for voice
4. **Use Conversation History**: The skill remembers recent chats for context

### For Development:

1. **Check Logs**: CloudWatch logs show which AI provider is being used
2. **DynamoDB Tables**: Stores user preferences and conversation history
3. **Error Handling**: Falls back gracefully if an AI provider is unavailable

---

## 🐛 Troubleshooting

### "I didn't quite catch that"
- API key may be missing or invalid
- Check Lambda environment variables
- Verify DynamoDB table exists

### Shopping Not Working
- This is expected for non-shopping queries!
- Use explicit shopping words: "find", "buy", "shop for"

### Wrong AI Provider Responding
- Set your default: "Set Gemini as my default"
- Or specify in query: "Use Claude to..."

### Skill Not Updating
1. Redeploy: `.\deploy-friendly-chat.ps1`
2. Clear Alexa cache: Say "Alexa, exit" and reopen
3. Check Lambda logs in CloudWatch

---

## 📈 Next Steps

1. ✅ Deploy the new Lambda function
2. ✅ Set up API keys
3. ✅ Test basic conversations
4. ✅ Try all three AI providers
5. ✅ Test shopping as secondary feature
6. 🎉 Enjoy your friendly AI assistant!

---

## 🤝 Support

- **Lambda Function**: `lambda_ai_pro_friendly_chat.py`
- **Deployment**: `deploy-friendly-chat.ps1`
- **Shopping Tools**: `shopping_tools.py` (unchanged)

Need help? Check CloudWatch Logs in AWS Console for detailed error messages.

---

## 🎉 You're All Set!

Your AI Pro skill is now a friendly, knowledgeable companion that can:
- ✅ Discuss any topic with enthusiasm
- ✅ Use multiple AI providers for diverse perspectives
- ✅ Remember conversation context
- ✅ Help with shopping when needed
- ✅ Provide a delightful user experience

**Try it now:**
"Alexa, open AI Pro"
"Tell me something fascinating!"

Enjoy! 🚀

