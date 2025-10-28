# 🐛 BUG BOUNTY: APL Dark Display Issue

## **Bounty Status:** 🔴 OPEN

---

## **Problem Statement**

The Alexa APL (Alexa Presentation Language) display is showing a **BLACK/DARK screen** on Echo Show devices and in the Alexa Developer Console simulator, despite multiple attempts to change the background to bright white.

### **Impact:**
- **Critical** - Users cannot see product information on screen
- **UX Blocker** - Shopping experience severely degraded
- **Launch Blocker** - Cannot release to production with this issue

---

## **Current Behavior (ACTUAL):**

### In Alexa Simulator:
- **Left Panel (Voice):** ✅ Works perfectly - shows products, prices, ratings
- **Right Panel (Device Display):** ❌ Shows BLACK screen with minimal text
- **Expected APL:** Should show bright white background with product cards

### On Physical Echo Show Device:
- **Voice Response:** ✅ Working - correct products announced
- **Visual Display:** ❌ Shows dark/black theme
- **Expected:** Bright white background with readable product information

---

## **Expected Behavior (SHOULD BE):**

### Visual Display Should Show:
- ✅ **WHITE background** (#ffffff)
- ✅ **Light gray product cards** (#f7fafc)
- ✅ **Purple header bar** (#667eea) with "🛍️ Shopping: [query]"
- ✅ **Product images** clearly visible
- ✅ **Dark text** on light background (readable)
- ✅ **Green prices** (#48bb78)
- ✅ **Orange star ratings** (#f6ad55)
- ✅ **Purple "Add item" buttons** (#667eea)

---

## **Technical Details**

### Current Lambda Configuration:
```json
{
  "FunctionName": "ai-pro-alexa-skill",
  "Runtime": "python3.11",
  "Handler": "lambda_ai_pro_secure.lambda_handler",
  "Memory": 1024,
  "Timeout": 30,
  "Region": "us-east-1"
}
```

### APL Tokens (Cache Busters):
- Product List: `shopping-products-bright-v2`
- Shopping Cart: `shopping-cart-bright-v2`
- Order Confirmation: `order-confirmation-bright-v2`

### APL Version:
```json
{
  "type": "APL",
  "version": "2023.3"
}
```

### Current Background Code:
```python
"background": "#ffffff"  # Should be pure white
```

---

## **What We've Tried (All Failed):**

1. ✅ **Changed background colors** from dark (#0f0f23) to white (#ffffff)
2. ✅ **Changed all gradients** to solid colors
3. ✅ **Updated card backgrounds** to light (#f7fafc)
4. ✅ **Changed text colors** to dark (#2d3748)
5. ✅ **Removed complex LinearGradient** objects
6. ✅ **Changed APL tokens** to force cache bypass
7. ✅ **Increased opacity** of transparent elements
8. ✅ **Redeployed Lambda** multiple times
9. ✅ **Refreshed simulator** browser
10. ✅ **Started fresh sessions**

### All Changes Deployed:
- Lambda last updated: 2025-10-28T01:26:48
- CodeSize: 19770 bytes
- Status: Successful, State: Active

---

## **Potential Root Causes to Investigate:**

### 1. APL Document Structure Issue
- **Check:** APL JSON syntax errors
- **Look for:** Invalid property names, wrong nesting
- **Verify:** APL version 2023.3 compatibility

### 2. Python String Interpolation Bug
- **Check:** F-strings in APL document
- **Issue:** `f"🛍️ Shopping: {query}"` might not work in APL JSON
- **Verify:** Are f-strings being evaluated before APL send?

### 3. APL Datasources Not Binding
- **Check:** `${payload.products}` bindings
- **Issue:** If datasources fail, APL might render blank/black
- **Verify:** Datasources structure matches APL expectations

### 4. Simulator APL Rendering Bug
- **Check:** Does APL work on REAL Echo Show device?
- **Issue:** Simulator might have rendering bugs
- **Test:** On physical device with same APL

### 5. APL Property Compatibility
- **Check:** Are all APL properties valid for version 2023.3?
- **Issue:** `boxShadow`, `direction`, etc. might not work
- **Verify:** Against official APL documentation

### 6. Background Color Format
- **Check:** Should be `"background": {"color": "#ffffff"}` instead of `"background": "#ffffff"`?
- **Issue:** Direct color assignment vs object format
- **Test:** Try both formats

### 7. Lambda Response Format
- **Check:** Is APL being sent in correct response structure?
- **Issue:** Response format might be wrong for APL
- **Verify:** Against Alexa skill response specification

### 8. Device Capability Mismatch
- **Check:** Is device capability check working?
- **Issue:** Code might detect "no APL support" and skip rendering
- **Verify:** supportedInterfaces contains Alexa.Presentation.APL

---

## **Files to Investigate:**

### Primary Files:
1. **`lambda_ai_pro_secure.py`**
   - Lines 124-270: `get_apl_document_products()` function
   - Lines 272-397: `get_apl_document_cart()` function
   - Lines 399-490: `get_apl_document_confirmation()` function
   - Lines 605-615: APL directive being sent

2. **`alexa-apl-purchase-flow.json`**
   - Standalone APL document (might be different from Lambda APL)

3. **CloudWatch Logs:**
   - Log group: `/aws/lambda/ai-pro-alexa-skill`
   - Look for: APL rendering errors, JSON syntax errors

---

## **Debug Tools & Methods:**

### 1. APL Authoring Tool
- **URL:** https://developer.amazon.com/alexa/console/ask/displays
- **Use:** Paste APL JSON and test rendering
- **Benefit:** Shows syntax errors immediately

### 2. CloudWatch Logs
```bash
aws logs tail /aws/lambda/ai-pro-alexa-skill --since 5m --follow
```

### 3. Lambda Test Event
```json
{
  "session": {
    "user": {"userId": "test-user"},
    "attributes": {}
  },
  "request": {
    "type": "IntentRequest",
    "intent": {
      "name": "ShoppingIntent",
      "slots": {
        "Product": {"value": "headphones"}
      }
    }
  },
  "context": {
    "System": {
      "device": {
        "supportedInterfaces": {
          "Alexa.Presentation.APL": {
            "runtime": {"maxVersion": "2023.3"}
          }
        }
      }
    }
  }
}
```

### 4. APL Response Validator
- Extract APL document from Lambda response
- Validate JSON syntax
- Test in APL Authoring Tool

---

## **Success Criteria:**

The bug is considered **RESOLVED** when:

1. ✅ **Simulator shows WHITE background** (not black)
2. ✅ **Product cards visible** with images and text
3. ✅ **Text is readable** (dark text on light background)
4. ✅ **No white screen** errors
5. ✅ **Works on physical Echo Show** device
6. ✅ **Consistent** across all APL screens (products, cart, confirmation)

---

## **Research Checklist:**

### Phase 1: Validate APL Syntax
- [ ] Copy APL JSON from Lambda
- [ ] Paste into APL Authoring Tool
- [ ] Check for syntax errors
- [ ] Verify all properties are valid
- [ ] Test rendering in authoring tool

### Phase 2: Check Lambda Response
- [ ] Add logging to print APL document before sending
- [ ] Verify APL is being included in response
- [ ] Check directive structure is correct
- [ ] Verify datasources match APL expectations

### Phase 3: Compare Working vs. Broken
- [ ] Find a working APL example (dark theme worked!)
- [ ] Compare JSON structure
- [ ] Identify what changed
- [ ] Test minimal APL (just background color change)

### Phase 4: Test Device Capabilities
- [ ] Log supportedInterfaces from event
- [ ] Verify APL capability detection
- [ ] Check if APL is being skipped due to capability check
- [ ] Test with explicit APL support check

### Phase 5: Incremental Changes
- [ ] Start with KNOWN working APL (dark theme)
- [ ] Change ONLY background color
- [ ] Deploy and test
- [ ] If works, change one more thing
- [ ] Repeat until bright theme works

---

## **Key Questions to Answer:**

1. **Is the APL being sent at all?**
   - Check: Lambda logs show APL in response?
   - Check: Alexa receiving the APL directive?

2. **Is the APL syntactically valid?**
   - Check: Paste in APL Authoring Tool
   - Check: Any JSON parsing errors?

3. **Are f-strings causing issues?**
   - Check: Does `f"Shopping: {query}"` work in APL?
   - Test: Replace with hardcoded string

4. **Is background format correct?**
   - Check: `"background": "#ffffff"` vs `"background": {"color": "#ffffff"}`
   - Test: Both formats

5. **Are there unsupported APL properties?**
   - Check: `boxShadow` supported in 2023.3?
   - Check: All properties against APL docs

---

## **Reference Documentation:**

- **APL Reference:** https://developer.amazon.com/docs/alexa-presentation-language/apl-overview.html
- **APL Component Properties:** https://developer.amazon.com/docs/alexa-presentation-language/apl-component.html
- **APL Authoring Tool:** https://developer.amazon.com/alexa/console/ask/displays
- **Skill Response Format:** https://developer.amazon.com/docs/custom-skills/request-and-response-json-reference.html

---

## **Known Working Code (Dark Theme):**

```python
# This APL worked (but was dark):
{
    "type": "Container",
    "background": {
        "type": "LinearGradient",
        "colorRange": ["#0f0f23", "#1a1a2e", "#16213e"]
    }
}
```

## **Target Code (Bright Theme - Not Working):**

```python
# This APL should work (but shows black):
{
    "type": "Container",
    "background": "#ffffff"
}
```

---

## **Hypothesis:**

The issue might be that:
1. **APL document has syntax error** → White screen/black fallback
2. **F-string interpolation fails** → APL never renders
3. **Datasources mismatch** → APL can't bind data → shows nothing
4. **Background shorthand not supported** → Needs full object format

---

## **Next Steps for Investigation:**

### Immediate:
1. **Extract exact APL JSON** being sent from Lambda
2. **Test in APL Authoring Tool** to validate syntax
3. **Compare with known-working dark APL**
4. **Identify the breaking change**

### If Syntax is Valid:
1. **Test minimal APL** (just container with white background)
2. **Add components incrementally** until it breaks
3. **Identify the problematic component**

### If Still Fails:
1. **Check Alexa skill configuration** for APL interface
2. **Verify Lambda permissions** for APL directives
3. **Test on different device** (real Echo Show vs simulator)

---

## **How to Submit Solution:**

When you find the fix:
1. **Document the root cause**
2. **Provide the working code**
3. **Explain why it was failing**
4. **Test to confirm it works**
5. **Share your findings**

---

## **Reward:**

When resolved:
- 🏆 **Credit in codebase**
- 📚 **Add to documentation**
- 🎯 **Complete the MVP launch**
- 💰 **Get the skill to market faster**

---

## **Current Status:**

**Lambda:** ✅ Deployed, Active, No Errors  
**Voice:** ✅ Working perfectly  
**APL:** ❌ Not rendering or showing dark/black  
**Priority:** 🔴 **Critical** - Blocking launch  

---

## **Good Luck!** 🔍

The answer is in there somewhere. My bet is on:
1. **F-string interpolation issue** in APL JSON, or
2. **Datasources binding problem**, or
3. **APL property compatibility** with version 2023.3

**Report back with your findings!** 🕵️

---

**Files to examine:**
- `lambda_ai_pro_secure.py` (lines 124-490)
- CloudWatch logs: `/aws/lambda/ai-pro-alexa-skill`
- APL Authoring Tool: Test the exact JSON being generated

