# AI Pro General Assistant - Deployment Guide

## 🎯 What This Does

Transforms AI Pro into a **friendly conversational AI** that can:
- Chat about anything (weather, jokes, facts, questions)
- Intelligently detect when you want to shop
- Seamlessly switch between chat and shopping modes
- Remember conversation context
- Maintain your shopping cart

---

## 🚀 Quick Deployment

### Step 1: Set Up Environment Variables

Add these to your Lambda function:

```bash
OPENAI_API_KEY=sk-...           # Your OpenAI API key
ANTHROPIC_API_KEY=sk-ant-...    # (Optional) For Claude
GOOGLE_API_KEY=AI...            # (Optional) For Gemini
DYNAMODB_TABLE=ai-assistant-users-dev
AMAZON_PARTNER_TAG=aipro00-20
```

### Step 2: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (starts with `sk-...`)
4. Add to Lambda environment variables

### Step 3: Deploy Lambda Function

```bash
# Package the function
cd "C:\Users\senti\OneDrive\Desktop\AI Pro Skill"
Compress-Archive -Path "lambda_ai_pro_general.py","shopping_tools.py" -DestinationPath "lambda-general-ai.zip" -Force

# Deploy to AWS
aws lambda update-function-code \
  --function-name ai-pro-alexa-skill \
  --zip-file fileb://lambda-general-ai.zip

# Update environment variables
aws lambda update-function-configuration \
  --function-name ai-pro-alexa-skill \
  --environment "Variables={OPENAI_API_KEY=sk-your-key-here,DYNAMODB_TABLE=ai-assistant-users-dev,AMAZON_PARTNER_TAG=aipro00-20}"
```

---

## 💬 How It Works

### Conversation Flow

**Launch:**
```
User: "Alexa, open AI Pro"
AI Pro: "Hi! I'm AI Pro, your friendly assistant. I can chat about anything, 
        help you shop on Amazon, or manage your cart. What's on your mind?"
```

**General Chat:**
```
User: "What's the weather like today?"
AI Pro: "I don't have real-time weather data, but you can ask me anything else! 
        Want to know about a topic, need shopping help, or just want to chat?"

User: "Tell me a joke"
AI Pro: "Why don't scientists trust atoms? Because they make up everything! 😄"
```

**Smart Shopping Detection:**
```
User: "I need new headphones"
AI Pro: [Detects "need" + "headphones" = shopping intent]
        "Great! I found 10 awesome options for headphones. Item 1: Sony WH-1000XM5..."
        [Shows beautiful APL display]
```

**Hybrid Conversation:**
```
User: "What's quantum computing?"
AI Pro: "Quantum computing uses quantum mechanics principles..."

User: "Cool! Can you find me a book about it?"
AI Pro: [Switches to shopping mode]
        "Sure! I found 'Quantum Computing for Everyone' at $29.99..."
```

---

## 🧠 Smart Intent Detection

### Shopping Keywords
The system automatically detects shopping intent when you say:
- buy, purchase, shop, shopping
- find product, looking for, search for
- need, want to buy, show me
- price, cost, deal, sale, discount

### Cart Keywords
Automatically routes to cart management when you say:
- cart, checkout, my order
- add item, remove item, clear cart
- view cart, show cart

### Everything Else
Routes to general AI chat for:
- Questions about any topic
- Casual conversation
- Weather, news, facts
- Jokes, stories, advice

---

## 🎨 Friendly Features

### Randomized Welcome Messages
5 different welcome messages to keep it fresh:
1. "Hi! I'm AI Pro, your friendly assistant..."
2. "Hey there! I'm here to help with anything..."
3. "Welcome to AI Pro! Think of me as your helpful friend..."
4. "Hi! Ready to have a conversation..."
5. "Hey! I'm AI Pro - part conversational buddy..."

### Conversation Memory
- Remembers last 20 messages
- Maintains context across conversation
- Seamless topic switching

### Natural Language
- Conversational tone
- Voice-optimized responses (concise)
- Friendly and helpful personality

---

## 🧪 Testing

### Test General Chat

**In Alexa Developer Console:**
```
1. "Alexa, open AI Pro"
   → Should get friendly welcome

2. "What is artificial intelligence?"
   → Should get conversational AI response

3. "Tell me a joke"
   → Should get a joke

4. "What's 2+2?"
   → Should answer with context
```

### Test Shopping Mode

**In Alexa Developer Console:**
```
1. "I need wireless headphones"
   → Should detect shopping intent and show products

2. "Find me a laptop under $1000"
   → Should search and display results with price filter

3. "Show me gaming chairs"
   → Should display gaming chair products
```

### Test Hybrid Mode

**In Alexa Developer Console:**
```
1. "What's machine learning?"
   → General AI response

2. "Can you find me a book about machine learning?"
   → Should switch to shopping mode

3. "What's in my cart?"
   → Should show cart contents

4. "Tell me more about neural networks"
   → Should switch back to chat mode
```

---

## 💰 API Costs

### OpenAI (GPT-3.5-turbo)
- **Cost**: ~$0.002 per conversation (150 tokens)
- **Monthly Estimate**:
  - 100 users × 10 conversations/day = 1,000 conversations/day
  - 30,000 conversations/month = ~$60/month

### Cost Optimization
1. Use GPT-3.5-turbo (cheaper than GPT-4)
2. Limit max_tokens to 150 for voice responses
3. Cache common questions
4. Use shopping mode (free) whenever possible

---

## 🔧 Advanced Configuration

### Switch to Anthropic Claude

Update the function to use Claude instead:

```python
def call_claude(prompt, user_id):
    """Call Anthropic Claude API"""
    # Implementation using Claude API
    pass
```

### Use Google Gemini

Update the function to use Gemini:

```python
def call_gemini(prompt, user_id):
    """Call Google Gemini API"""
    # Implementation using Gemini API
    pass
```

### Multi-Model Support

Let users choose their preferred AI:
```
User: "Set my AI to Claude"
AI Pro: "Great! I'll use Claude for our conversations now."
```

---

## 🎯 Interaction Model Updates

### Add Fallback Intent

In `alexa-interaction-model-complete.json`, ensure you have:

```json
{
  "name": "AMAZON.FallbackIntent",
  "samples": []
}
```

This catches any unmatched utterances and routes them to general AI chat.

### Update LLMQueryIntent

```json
{
  "name": "LLMQueryIntent",
  "slots": [
    {
      "name": "Query",
      "type": "AMAZON.SearchQuery"
    }
  ],
  "samples": [
    "{Query}",
    "what is {Query}",
    "tell me about {Query}",
    "explain {Query}",
    "what's {Query}",
    "how does {Query} work"
  ]
}
```

---

## 🚨 Troubleshooting

### Issue: "I'd love to chat, but I need an API key configured"
**Solution**: Add `OPENAI_API_KEY` to Lambda environment variables

### Issue: Responses are too long for voice
**Solution**: Reduce `max_tokens` in OpenAI call (currently 150)

### Issue: Not detecting shopping intent
**Solution**: Check `SHOPPING_KEYWORDS` list, add more keywords if needed

### Issue: Conversation context not saved
**Solution**: Check DynamoDB permissions for the Lambda role

---

## 📊 Monitoring

### CloudWatch Metrics to Watch
- **Intent Detection**: Check logs for "Detected intent: chat/shopping/cart"
- **API Calls**: Monitor OpenAI API usage
- **Response Times**: Ensure < 3 seconds for voice
- **Error Rates**: Watch for API failures

### Custom Logging
The function logs:
```
"User query: [query]"
"Detected intent: [chat/shopping/cart]"
"OpenAI error: [error message]"
```

---

## 🎉 Success Checklist

- [ ] OpenAI API key added to Lambda
- [ ] Lambda function deployed
- [ ] Test general chat: "What is AI?"
- [ ] Test shopping: "Find me headphones"
- [ ] Test cart: "What's in my cart?"
- [ ] Test hybrid: Chat → Shopping → Chat
- [ ] Verify conversation memory works
- [ ] Check CloudWatch logs

---

## 🚀 Next Steps

### Phase 1: Basic Testing (Now)
Test all conversation modes and verify intent detection

### Phase 2: Enhanced Features (Week 2)
- Add personality customization
- Implement multi-turn conversations
- Add product recommendations based on chat

### Phase 3: Advanced AI (Week 3)
- Switch between OpenAI/Claude/Gemini
- Voice tone analysis
- Personalized responses

### Phase 4: Analytics (Week 4)
- Track popular questions
- Measure shopping conversion from chat
- Optimize API costs

---

## 💡 Pro Tips

1. **Start conversations naturally**: Don't immediately ask for shopping
2. **Build rapport**: Chat first, then suggest products naturally
3. **Context matters**: Use conversation history to make better recommendations
4. **Be helpful**: Offer shopping when relevant, chat when not

---

## 🆘 Need Help?

**Common Questions:**
- How to reduce API costs? → Use GPT-3.5, limit tokens, cache responses
- How to add more LLM providers? → Add functions for Claude/Gemini
- How to improve intent detection? → Update keyword lists, use AI classification

**Resources:**
- OpenAI Documentation: https://platform.openai.com/docs
- Lambda Best Practices: AWS Lambda docs
- APL Documentation: Alexa APL docs

---

**You're now ready to launch AI Pro as a friendly general assistant! 🎉**

