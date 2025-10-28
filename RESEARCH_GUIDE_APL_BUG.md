# 🔬 Research Guide: APL Dark Display Bug

## **Start Here:**

Run the diagnostic tool to extract the exact APL being sent:

```powershell
python diagnostic_extract_apl.py
```

This will create `extracted_apl_document.json` - the **exact APL** your Lambda is generating.

---

## **Research Path 1: Validate APL Syntax**

### Step 1: Test in APL Authoring Tool
1. Go to: https://developer.amazon.com/alexa/console/ask/displays
2. Click **"Start from Scratch"**
3. Paste contents of `extracted_apl_document.json`
4. Click **"Preview"**

**What to look for:**
- ✅ **Green success** → APL is valid, issue is elsewhere
- ❌ **Red error** → Shows exact line with syntax error
- ⚠️ **Renders dark** → APL is valid but colors are wrong in the JSON

### Step 2: Minimal Test
Create the simplest possible white APL:

```json
{
  "type": "APL",
  "version": "2023.3",
  "mainTemplate": {
    "items": [
      {
        "type": "Container",
        "width": "100vw",
        "height": "100vh",
        "background": "#ffffff",
        "items": [
          {
            "type": "Text",
            "text": "WHITE TEST",
            "fontSize": 50,
            "color": "#000000",
            "textAlign": "center"
          }
        ]
      }
    ]
  }
}
```

If this shows WHITE in authoring tool → Syntax is fine!

---

## **Research Path 2: F-String Investigation**

### The Suspect:
```python
"text": f"🛍️ Shopping: {query}"
```

### Problem:
Python f-strings are evaluated **when Python runs**, but this is inside a **dictionary that becomes JSON**. The emoji might be causing encoding issues.

### Test:
1. Search for all `f"` in `lambda_ai_pro_secure.py`
2. Replace with regular strings:
   ```python
   # Before:
   "text": f"🛍️ Shopping: {query}"
   
   # After:
   "text": "Shopping: " + query  # No emoji, no f-string
   ```

3. Redeploy and test

### Check Encoding:
```python
# Is the emoji breaking JSON encoding?
test_emoji = "🛍️"
print(test_emoji.encode('utf-8'))  # Should work
print(json.dumps({"text": "🛍️"}))  # Should work
```

---

## **Research Path 3: Background Property Format**

### APL Spec Says:
Background can be:
1. **Color string**: `"background": "#ffffff"` ✅
2. **Gradient object**: `"background": {"type": "LinearGradient", ...}` ✅
3. **Color object**: `"background": {"type": "Color", "color": "#ffffff"}` ✅

### Test Each Format:

**Format 1 (Current):**
```json
"background": "#ffffff"
```

**Format 2 (Explicit):**
```json
"background": {
  "type": "Color",
  "color": "#ffffff"
}
```

**Format 3 (Gradient):**
```json
"background": {
  "type": "LinearGradient",
  "colorRange": ["#ffffff", "#f5f7fa"],
  "inputRange": [0, 1],
  "angle": 0
}
```

Test each in APL Authoring Tool!

---

## **Research Path 4: Check What's Actually Being Sent**

### Add Debug Logging:

In `lambda_ai_pro_secure.py`, line 609, add:

```python
'document': get_apl_document_products(products, product),

# Add this right after:
import logging
logger = logging.getLogger()
logger.info(f"APL DOCUMENT: {json.dumps(get_apl_document_products(products, product))}")
```

Then check CloudWatch:
```bash
aws logs tail /aws/lambda/ai-pro-alexa-skill --since 5m | grep "APL DOCUMENT"
```

This shows you **exactly** what APL is being sent!

---

## **Research Path 5: Device Capability Check**

### Check This Code:

Around line 585-595 in lambda_ai_pro_secure.py:

```python
# Is this code detecting APL support correctly?
supports_display = True  # Hardcoded?
```

### Look For:
```python
if 'context' in event and 'System' in event['context']:
    system = event['context']['System']
    if 'device' in system and 'supportedInterfaces' in system['device']:
        supported_interfaces = system['device']['supportedInterfaces']
        supports_display = 'Alexa.Presentation.APL' in supported_interfaces
```

### The Question:
Is `supports_display` being set to `False`? Then APL never gets sent!

Add logging:
```python
logger.info(f"SUPPORTS DISPLAY: {supports_display}")
logger.info(f"SUPPORTED INTERFACES: {supported_interfaces}")
```

---

## **Research Path 6: Compare Lambda Response Format**

### Correct Format:
```python
{
    'version': '1.0',
    'sessionAttributes': {},
    'response': {
        'outputSpeech': {...},
        'card': {...},
        'directives': [
            {
                'type': 'Alexa.Presentation.APL.RenderDocument',
                'token': 'shopping-products-bright-v2',
                'document': {...},  # The APL JSON
                'datasources': {...}
            }
        ],
        'shouldEndSession': False
    }
}
```

### Check:
- Is `directives` array present?
- Is it inside `response`?
- Is directive type exactly `'Alexa.Presentation.APL.RenderDocument'`?

---

## **Quick Wins to Try:**

### 1. Test Without Emoji
Remove `🛍️` from APL:
```python
"text": f"Shopping: {query}"  # No emoji
```

### 2. Test Without F-String
```python
"text": "Shopping: headphones"  # Hardcoded
```

### 3. Test Minimal APL
Replace entire `get_apl_document_products()` with:
```python
def get_apl_document_products(products, query):
    return {
        "type": "APL",
        "version": "2023.3",
        "mainTemplate": {
            "items": [
                {
                    "type": "Text",
                    "text": "TEST WHITE",
                    "fontSize": 50
                }
            ]
        }
    }
```

If this works → Problem is in complex APL structure!

---

## **Common APL Gotchas:**

1. **Quotes in f-strings:**
   - Bad: `f"text: {value}"`  inside JSON
   - Good: Use `.format()` or concatenation

2. **Python dict to JSON:**
   - Python `True` ≠ JSON `true`
   - Python `None` ≠ JSON `null`

3. **Special characters:**
   - Emojis might need Unicode escaping
   - Check: `\u{codepoint}` format

4. **Properties not in spec:**
   - `boxShadow` - Is this supported?
   - `direction` - Check version compatibility

---

## **Tools You'll Need:**

1. **APL Authoring Tool** (test APL syntax)
2. **CloudWatch** (see exact Lambda output)
3. **JSON Validator** (check JSON syntax)
4. **Diagnostic script** (extract APL)
5. **Working dark APL** (for comparison)

---

## **Expected Timeline:**

- **30 min:** Extract and validate APL JSON
- **1 hour:** Test in authoring tool, find syntax issue
- **30 min:** Fix and redeploy
- **TOTAL:** ~2 hours to resolution

---

## **Report Template:**

When you find it, document:

```markdown
## BUG FOUND!

**Root Cause:** [What was wrong]

**Location:** lambda_ai_pro_secure.py line [X]

**The Problem:**
[Explain the issue]

**The Fix:**
[Show the code change]

**Why It Failed:**
[Technical explanation]

**Verification:**
[How you tested it works]
```

---

**Good luck with your research!** 🔍

Start with the diagnostic tool to extract the APL, then test in the APL Authoring Tool. That will tell you exactly what's wrong!
