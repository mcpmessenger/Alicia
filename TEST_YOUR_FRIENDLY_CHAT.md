# 🧪 Test Your Friendly Chat Assistant

## Quick Test Guide

After deploying, use these test queries to verify everything works!

---

## ✅ Test Checklist

### 1. Launch & Welcome Message
**Say**: `"Alexa, open AI Pro"`

**Expected**: Friendly welcome message like:
- "Hey! I'm AI Pro. I love chatting about anything..."
- "Hi there! Ready to explore some interesting topics?"

**✓ PASS**: You get a casual, friendly greeting (NOT about shopping)  
**✗ FAIL**: If it says "Welcome to AI Pro Shopping..."

---

### 2. General Knowledge (Chat Mode - Default)

#### Test A: Simple Question
**Say**: `"What is artificial intelligence?"`

**Expected**: Conversational explanation about AI

**✓ PASS**: Gets detailed, friendly answer  
**✗ FAIL**: Says "Your cart is empty" or tries to search products

---

#### Test B: Science Question
**Say**: `"Tell me about black holes"`

**Expected**: Engaging explanation about black holes

**✓ PASS**: Informative, voice-friendly response  
**✗ FAIL**: Product search or error

---

#### Test C: History Question
**Say**: `"What happened in 1969?"`

**Expected**: Information about moon landing, Woodstock, etc.

**✓ PASS**: Historical information  
**✗ FAIL**: Shopping response

---

### 3. Multi-AI Provider Testing

#### Test D: Use Gemini
**Say**: `"Use Gemini to explain quantum physics"`

**Expected**: Response from Google Gemini

**✓ PASS**: Gemini-powered response  
**✗ FAIL**: Error or wrong provider

---

#### Test E: Use Claude
**Say**: `"Ask Claude about philosophy"`

**Expected**: Response from Anthropic Claude

**✓ PASS**: Claude-powered response  
**✗ FAIL**: Error or wrong provider

---

#### Test F: Use OpenAI
**Say**: `"Use OpenAI to write me a haiku"`

**Expected**: OpenAI GPT response with a haiku

**✓ PASS**: Gets haiku  
**✗ FAIL**: Error or no haiku

---

### 4. Set AI Preference

#### Test G: Set Default Provider
**Say**: `"Set Gemini as my default"`

**Expected**: Confirmation like "Got it! I'll use Gemini by default now"

**✓ PASS**: Confirms preference saved  
**✗ FAIL**: Error or doesn't save

---

### 5. Shopping (Secondary Feature)

#### Test H: Explicit Shopping Request
**Say**: `"Find me wireless headphones"`

**Expected**: 
- Product search results
- Visual display (if device has screen)
- Voice readout of top 3 products

**✓ PASS**: Shows products  
**✗ FAIL**: No products or error

---

#### Test I: Add to Cart
**Say**: `"Add item 1"`

**Expected**: "Added [product name] to your cart!"

**✓ PASS**: Product added  
**✗ FAIL**: Error or item not added

---

#### Test J: View Cart
**Say**: `"View my cart"`

**Expected**: "You have X items totaling $Y"

**✓ PASS**: Shows cart contents  
**✗ FAIL**: Error or wrong info

---

### 6. Context & Memory

#### Test K: Follow-up Question
**Say**: `"Tell me about Mars"`

**Expected**: Information about Mars

**Then say**: `"What about its moons?"`

**Expected**: Should understand context (Mars's moons)

**✓ PASS**: Contextual response  
**✗ FAIL**: Loses context

---

### 7. Edge Cases

#### Test L: Non-Shopping Query (Should NOT Trigger Shopping)
**Say**: `"Tell me a poem about lizards"`

**Expected**: Actual poem, NOT "Your cart is empty"

**✓ PASS**: Gets poem  
**✗ FAIL**: Shopping response

---

#### Test M: Ambiguous Query
**Say**: `"Tell me something interesting"`

**Expected**: Shares an interesting fact or topic

**✓ PASS**: Engaging response  
**✗ FAIL**: Error or confusion

---

#### Test N: Help Command
**Say**: `"Help"`

**Expected**: Explanation of capabilities (chat, research, shopping)

**✓ PASS**: Helpful guidance  
**✗ FAIL**: Only mentions shopping

---

## 📊 Test Results Summary

Fill this out as you test:

```
✓ Launch & Welcome              [ ]
✓ General Knowledge             [ ]
✓ Science Question              [ ]
✓ History Question              [ ]
✓ Use Gemini                    [ ]
✓ Use Claude                    [ ]
✓ Use OpenAI                    [ ]
✓ Set Default Provider          [ ]
✓ Shopping Search               [ ]
✓ Add to Cart                   [ ]
✓ View Cart                     [ ]
✓ Context Memory                [ ]
✓ Non-Shopping Query            [ ]
✓ Ambiguous Query               [ ]
✓ Help Command                  [ ]

Total Passed: ___/15
```

---

## 🐛 Troubleshooting

### Issue: "I didn't understand that"

**Possible Causes:**
1. API key not configured
2. DynamoDB table doesn't exist
3. Lambda function not deployed

**Fix:**
```bash
# Check Lambda environment variables
aws lambda get-function-configuration --function-name ai-pro-skill --region us-east-1

# Verify API keys are set
# Should show OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY
```

---

### Issue: Still Getting Shopping Responses for Chat

**Possible Causes:**
1. Old Lambda code still deployed
2. Cache not cleared

**Fix:**
```powershell
# Redeploy
.\deploy-friendly-chat.ps1

# Then test in Alexa console
# Say "Alexa, exit" and reopen skill
```

---

### Issue: AI Provider Not Working

**Possible Causes:**
1. API key invalid
2. API quota exceeded
3. Wrong API key format

**Fix:**
```bash
# Test API key directly
# OpenAI:
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"

# Should return list of models if key is valid
```

---

### Issue: Shopping Not Working

**Possible Causes:**
1. Intent detection too strict
2. Product catalog not loaded

**Fix:**
- Use explicit shopping words: "find", "search for", "buy"
- Example: "Find me headphones" (not "headphones")

---

## 🔍 Check AWS CloudWatch Logs

For detailed debugging:

1. Go to AWS Console
2. CloudWatch → Log Groups
3. Find `/aws/lambda/ai-pro-skill`
4. Look for recent log streams
5. Search for:
   - `"Using AI provider:"` - Shows which AI is being used
   - `"Shopping intent detected"` - Shows shopping triggers
   - `"General chat intent"` - Shows chat mode
   - Errors or exceptions

---

## ✅ Success Criteria

Your skill is working perfectly if:

1. ✅ Welcome message is friendly and casual (not shopping-focused)
2. ✅ Can answer general knowledge questions
3. ✅ Can use different AI providers (Gemini, Claude, OpenAI)
4. ✅ Shopping only activates with explicit shopping words
5. ✅ Poem query returns a poem (not cart message!)
6. ✅ Remembers conversation context
7. ✅ All 15 tests pass

---

## 🎉 When All Tests Pass

Congratulations! Your AI Pro skill is now:
- 🧠 Knowledgeable on any topic
- 💬 Great for conversations
- 🤖 Powered by multiple AI providers
- 🛍️ Can help with shopping when needed
- 🎯 User-friendly and engaging

**Share it with friends!**  
**Ask it interesting questions!**  
**Enjoy your new AI companion!**

---

## 📝 Advanced Testing

Once basics work, try:

### Complex Queries
- "Compare quantum mechanics and relativity"
- "Explain machine learning to a 10-year-old"
- "What's the history of computers?"

### Multi-Turn Conversations
- "Tell me about the solar system"
- "Which planet is largest?"
- "Tell me more about its moons"

### Provider Comparison
- "Use Gemini to explain AI"
- "Now ask Claude the same thing"
- "Compare their answers"

### Shopping + Chat Mix
- "Tell me about audio technology"
- "Now find me headphones with good reviews"
- "Tell me more about noise cancellation"

---

**Happy Testing! 🚀**

If all tests pass, you've successfully transformed your skill from a shopping assistant into an engaging AI companion!

