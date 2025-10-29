# Force Console to Use New APL - Quick Steps

## Issue
Console showing old black APL despite Lambda having correct white background code.

## Solution: Force Fresh Request

### Step 1: Go Back to Test Tab
Click the **"Test"** tab at the top

### Step 2: Clear Simulator History
In the Alexa Simulator (left side), scroll up to the top and you should see conversation history. We need to start completely fresh.

### Step 3: Type "exit" first
In the input box at the bottom, type:
```
exit
```
Press Enter. This will close the skill session.

### Step 4: Wait 5 seconds
Let the session fully close.

### Step 5: Relaunch with Fresh Request
Type:
```
open ai pro
```
Press Enter.

### Step 6: Trigger Shopping
Type:
```
show me headphones
```

This should trigger a FRESH Lambda invocation with the new APL code.

## Alternative: Hard Refresh Browser

If the above doesn't work:

1. Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
2. Wait for page to fully reload
3. Go back to Test tab
4. Try the requests again

## What You Should See

After the fresh request, the APL display on the right should show:
- ✅ **WHITE background** (not black!)
- ✅ Purple header: "🛍️ Shopping: headphones"
- ✅ Light gray product cards
- ✅ Product information with images

## Still Black?

If it's STILL black after a fresh request, check the "Manual JSON" tab to see the actual response from Lambda.


