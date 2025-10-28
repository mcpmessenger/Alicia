# Testing Your Expanded Shopping Catalog

## 🌍 IMPORTANT: Use English (US) in Alexa Simulator!

Change dropdown to "English (US)" before testing.

---

## 🧪 Complete Shopping Flow Test

### Test 1: Basic Search
```
YOU: "open ai pro"
ALEXA: "Welcome to AI Pro Shopping!..."

YOU: "search for headphones"
EXPECTED: Shows 4 real headphone products with your affiliate links
```

### Test 2: Add to Cart
```
YOU: "add item 1"  (Sony headphones)
EXPECTED: "Added Sony WH-1000XM5 to your cart for $398. You have 1 item"

YOU: "add item 2"  (AirPods Pro)
EXPECTED: "Added Apple AirPods Pro to your cart for $249. You now have 2 items"
```

### Test 3: View Cart
```
YOU: "view cart"
EXPECTED: Shows both items with total of $647
```

### Test 4: Checkout
```
YOU: "checkout now"
EXPECTED: "You're about to purchase 2 items for $647. Say yes to confirm"

YOU: "yes, buy it"
EXPECTED: "Order confirmed! Order #XXXXX. Total: $647. Tracking: AIPRO-XXXXX"
```

### Test 5: Verify Cart Cleared
```
YOU: "view cart"
EXPECTED: "Your cart is empty"
```

---

## 🔍 Test Different Categories

### Electronics
- "search for headphones"
- "find me smart speakers"
- "show me airpods"
- "I want wireless headphones"

### Home & Kitchen
- "find me a coffee maker"
- "search for air fryer"
- "show me blenders"
- "I need an instant pot"

### Vacuums
- "search for vacuum"
- "find me a cordless vacuum"
- "show me shark vacuum"

### Fashion & Travel
- "find me a backpack"
- "search for luggage"
- "show me travel bags"

### Smart Devices
- "find echo dot"
- "search for fire tv"
- "show me ring doorbell"

### Fitness
- "find fitness tracker"
- "search for yoga mat"
- "show me water bottle"

---

## 💡 Smart Search Examples

### Price Filters
```
"find headphones under 100"
"search for vacuum under 200"
"show me coffee makers under 50"
```

### Category + Product
```
"find me electronics headphones"
"search for home vacuum"
"show me fitness tracker"
```

---

## 📊 What You Should See

### In Response:
1. **Product list** with up to 5 matches
2. Each product shows:
   - Name
   - Price (in green)
   - Rating (with stars)
   - Description
   - Your affiliate link

### In Alexa App:
- Clickable product links with your tag
- Product images
- Full details

### In DynamoDB:
- Cart items saved
- Order history saved
- All with your affiliate tracking

---

## 🚨 Troubleshooting

### "Can't find products"
- Check you're using English (US)
- Try more generic terms: "headphones" not "Sony WH-1000XM5"
- System searches based on keywords in product names

### "Wrong products showing"
- The search algorithm scores products by keyword relevance
- Products with your search terms in the name rank higher

### "Session issues"
- Cart persists across sessions
- Each user has their own cart
- DynamoDB stores everything

---

## 🎯 Quick Test Commands

```bash
# Test 1: Launch
"open ai pro"

# Test 2: Search
"search for headphones"

# Test 3: Add
"add item 1"
"add item 2"

# Test 4: Cart
"view cart"

# Test 5: Checkout
"checkout now"
"yes, buy it"
```

---

Ready to test! 🚀


