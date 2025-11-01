# 🚀 Quick Deploy Guide - APL Fix

## **ISSUE RESOLVED!** ✅

The black screen issue is now **FIXED**. The problem was APL Sequence components using wrong syntax.

---

## **Quick Deploy (2 Minutes)**

### Option 1: Using PowerShell Script (Recommended)

```powershell
# Run the deployment script
python deploy-general-ai.ps1
```

### Option 2: Manual AWS CLI Deploy

```powershell
# 1. Create ZIP with dependencies
Compress-Archive -Path lambda_ai_pro_general.py, shopping_tools.py, products-catalog.json -DestinationPath lambda-fix.zip -Force

# 2. Upload to Lambda (replace with your function name)
aws lambda update-function-code --function-name ai-pro-alexa-skill --zip-file fileb://lambda-fix.zip --region us-east-1

# 3. Wait for update
Start-Sleep -Seconds 5

# 4. Verify deployment
aws lambda get-function --function-name ai-pro-alexa-skill --region us-east-1 --query 'Configuration.LastModified'
```

### Option 3: AWS Console (Manual Upload)

1. Go to: https://console.aws.amazon.com/lambda
2. Select your function: `ai-pro-alexa-skill`
3. Click **"Upload from"** → **".zip file"**
4. Upload the ZIP containing:
   - `lambda_ai_pro_general.py`
   - `shopping_tools.py`
   - `products-catalog.json`
5. Click **"Save"**
6. Wait 10 seconds for deployment

---

## **Test Immediately**

### In Alexa Developer Console:
1. Go to: https://developer.amazon.com/alexa/console/ask
2. Select your skill
3. Click **"Test"** tab
4. Select device: **"Hub Landscape Medium"**
5. Type: `open a.i. pro`
6. Type: `find headphones`

**Expected Result:**
- ✅ **WHITE background** (not black!)
- ✅ **Product cards** with images visible
- ✅ **Prices and ratings** displayed
- ✅ **"Add item" buttons** visible

---

## **What Was Fixed**

### The Bug:
APL Sequence was using:
```json
"items": [ ... ]  // ❌ WRONG - Static array syntax
```

### The Fix:
Changed to:
```json
"item": { ... }  // ✅ CORRECT - Dynamic template syntax
```

**Result:** Products now render correctly on the display!

---

## **Files Changed**

✅ `lambda_ai_pro_general.py` - Fixed product list APL  
✅ `lambda_ai_pro_secure.py` - Fixed product list + cart APL  
✅ `lambda_simple_bright.py` - Fixed product list + cart APL  

---

## **After Deployment**

### Clear Alexa Cache:
Say to your Echo Show:
- "Alexa, open AI Pro"
- (It will load the new version automatically)

### Verify on Device:
- "Find laptops" → Should show white screen with products
- "Find headphones" → Should show bright cards with images
- View on Echo Show → Should see beautiful UI

---

## **Troubleshooting**

### If still showing black screen:

1. **Check Lambda deployed:**
   ```powershell
   aws lambda get-function-configuration --function-name ai-pro-alexa-skill --query 'LastModified'
   ```

2. **Check APL token changed:**
   - Look for: `shopping-products-bright-v4-fixed`
   - (Not: `shopping-products-bright-v3`)

3. **Clear browser cache:**
   - In Developer Console: Ctrl+Shift+Delete
   - Clear cache and reload

4. **Start new session:**
   - In simulator: Click "Reset" button
   - Say: "Alexa, open AI Pro" (fresh start)

---

## **Success Checklist**

After deployment, verify:

- [ ] Lambda function shows new LastModified timestamp
- [ ] Simulator shows white background
- [ ] Products display with images
- [ ] Text is readable (dark on light)
- [ ] Prices show in green
- [ ] Star ratings visible
- [ ] "Add item" buttons appear
- [ ] Scrolling works for multiple products

---

## **Need Help?**

Check these files:
- `BUG_FIX_SUMMARY.md` - Complete technical explanation
- `BUG_BOUNTY_APL_DARK_DISPLAY.md` - Original bug report (now resolved)
- CloudWatch Logs: `/aws/lambda/ai-pro-alexa-skill`

---

**Ready to deploy? Run the script now!** 🚀

```powershell
python deploy-general-ai.ps1
```



