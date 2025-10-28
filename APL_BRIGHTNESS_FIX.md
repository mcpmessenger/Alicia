# APL Display Brightness Fix

## Quick Fix for Dark Screen

If your Echo Show display is too dark to see, update the APL background colors:

### Current (Dark):
```json
"background": {
  "type": "LinearGradient",
  "colorRange": ["#0f0f23", "#1a1a2e", "#16213e"]
}
```

### Brighter Option 1 (Lighter):
```json
"background": {
  "type": "LinearGradient",
  "colorRange": ["#1a1a3e", "#2d2d5e", "#252555"]
}
```

### Brighter Option 2 (Much Lighter):
```json
"background": {
  "type": "LinearGradient",
  "colorRange": ["#2a2a4e", "#3d3d6e", "#353565"]
}
```

### Bright Mode (Light Theme):
```json
"background": {
  "type": "LinearGradient",
  "colorRange": ["#e8e8f0", "#f5f5fa", "#f0f0f5"]
}
```

Update these in:
- `alexa-apl-purchase-flow.json`
- Lambda functions: `get_apl_document_products()`, `get_apl_document_cart()`, etc.

Just find the "background" property and change the colorRange values!


