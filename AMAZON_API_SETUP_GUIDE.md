# Amazon Product Advertising API - Setup Guide

## Step 1: Create Amazon Associates Account

1. **Go to:** https://affiliate-program.amazon.com/
2. **Sign up** with your Amazon account
3. **Complete the application:**
   - Website/mobile app URL (you can use a placeholder like your-domain.com)
   - Preferred store ID (e.g., `yourname-20`)
   - How you drive traffic: "Voice shopping through Alexa skill"
4. **Wait for approval** (usually 24-48 hours, but you can start development immediately)

**Your Associate ID format:** `yourname-20` (the `-20` is standard for US)

---

## Step 2: Get PA-API Access Keys

1. **Go to:** https://webservices.amazon.com/paapi5/documentation/
2. Click **"Register for PA-API"**
3. **Sign in** with your Amazon Associates account
4. **Add your website** (same as Associates signup)
5. **Get your credentials:**
   - **Access Key** (looks like: `AKIAIOSFODNN7EXAMPLE`)
   - **Secret Key** (looks like: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
   - **Partner Tag** (your Associate ID: `yourname-20`)

**Important:** Keep these keys secret! Never commit to GitHub.

---

## Step 3: PA-API Requirements

### Eligible Associates
- Must have at least **3 qualified sales** within 180 days
- OR get approved for API access (sometimes granted immediately)

### API Limits
- **Free Tier:** 8,640 requests/day (1 request every 10 seconds)
- **Paid:** Up to 1 request/second with sales volume

---

## Step 4: Install PA-API Python SDK

The PA-API SDK needs to be included in your Lambda layer.

### Option A: Use pip (for local testing)
```bash
pip install python-amazon-paapi
```

### Option B: Create Lambda Layer (recommended)
```bash
mkdir -p python/lib/python3.11/site-packages
pip install python-amazon-paapi -t python/lib/python3.11/site-packages/
zip -r pa-api-layer.zip python/
```

Then upload as Lambda layer.

---

## Step 5: Test Your Credentials

```python
from amazon.paapi import AmazonAPI

# Test connection
api = AmazonAPI(
    access_key='YOUR_ACCESS_KEY',
    secret_key='YOUR_SECRET_KEY',
    partner_tag='yourname-20',
    country='US'
)

# Simple search
products = api.search_items(keywords='headphones')
print(products)
```

---

## Alternative: Use Amazon Associates Link Builder

If you can't get PA-API access immediately, you can use:
- **SiteStripe** (browser toolbar)
- **Link Builder** in Associates dashboard
- **Manual affiliate links**

Format: `https://www.amazon.com/dp/PRODUCT_ASIN?tag=yourname-20`

---

## Quick Start Checklist

- [ ] Amazon Associates account created
- [ ] Associate ID obtained (e.g., `yourname-20`)
- [ ] PA-API access requested
- [ ] Access Key obtained
- [ ] Secret Key obtained
- [ ] Credentials stored in AWS Secrets Manager or Lambda environment variables

---

## Security Best Practices

**Never hardcode credentials!** Use:

### Option 1: Lambda Environment Variables (Simple)
```bash
aws lambda update-function-configuration \
  --function-name ai-pro-alexa-skill \
  --environment Variables="{
    AMAZON_ACCESS_KEY=YOUR_KEY,
    AMAZON_SECRET_KEY=YOUR_SECRET,
    AMAZON_PARTNER_TAG=yourname-20
  }"
```

### Option 2: AWS Secrets Manager (Production)
```bash
aws secretsmanager create-secret \
  --name ai-pro/amazon-api \
  --secret-string '{"access_key":"YOUR_KEY","secret_key":"YOUR_SECRET","partner_tag":"yourname-20"}'
```

---

## Cost Breakdown

| Item | Cost |
|------|------|
| Amazon Associates | **FREE** |
| PA-API Access | **FREE** (with sales) |
| Lambda Execution | ~$0.20/1000 requests |
| **Total** | **~$0 to start** |

**Revenue:** 1-10% commission on sales through your affiliate links!

---

Next: See `shopping_tools_real_api.py` for implementation.

