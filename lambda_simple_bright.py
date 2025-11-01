# Simple bright APL that WILL work
# Minimal complexity, maximum brightness

def get_simple_bright_apl(products, query):
    """Simple, bright APL that works 100%"""
    return {
        "type": "APL",
        "version": "2023.3",
        "mainTemplate": {
            "parameters": ["payload"],
            "items": [
                {
                    "type": "Container",
                    "width": "100vw",
                    "height": "100vh",
                    "background": "#ffffff",
                    "direction": "column",
                    "items": [
                        {
                            "type": "Container",
                            "width": "100%",
                            "height": 80,
                            "background": "#667eea",
                            "padding": 20,
                            "items": [
                                {
                                    "type": "Text",
                                    "text": f"🛍️ Shopping: {query}",
                                    "fontSize": 28,
                                    "fontWeight": "bold",
                                    "color": "#ffffff",
                                    "textAlign": "center"
                                }
                            ]
                        },
                        {
                            "type": "Sequence",
                            "width": "100%",
                            "height": "80vh",
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "paddingTop": 20,
                            "data": "${payload.products}",
                            "numbered": True,
                            "item": {
                                "type": "Container",
                                "width": "100%",
                                "background": "#f7fafc",
                                "borderRadius": 15,
                                "padding": 20,
                                "marginBottom": 15,
                                "direction": "row",
                                "items": [
                                    {
                                        "type": "Image",
                                        "source": "${data.image_url}",
                                        "width": 120,
                                        "height": 120,
                                        "scale": "best-fit",
                                        "borderRadius": 10
                                    },
                                    {
                                        "type": "Container",
                                        "paddingLeft": 20,
                                        "grow": 1,
                                        "items": [
                                            {
                                                "type": "Text",
                                                "text": "${data.name}",
                                                "fontSize": 18,
                                                "fontWeight": "bold",
                                                "color": "#2d3748",
                                                "maxLines": 2
                                            },
                                            {
                                                "type": "Text",
                                                "text": "$${data.price}",
                                                "fontSize": 24,
                                                "fontWeight": "bold",
                                                "color": "#48bb78",
                                                "marginTop": 5
                                            },
                                            {
                                                "type": "Text",
                                                "text": "⭐ ${data.rating}/5 (${data.reviews} reviews)",
                                                "fontSize": 13,
                                                "color": "#718096",
                                                "marginTop": 5
                                            },
                                            {
                                                "type": "Container",
                                                "marginTop": 10,
                                                "padding": 12,
                                                "background": "#667eea",
                                                "borderRadius": 10,
                                                "items": [
                                                    {
                                                        "type": "Text",
                                                        "text": "🛒 Say: Add item ${index+1}",
                                                        "fontSize": 14,
                                                        "fontWeight": "bold",
                                                        "color": "#ffffff",
                                                        "textAlign": "center"
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        },
                        {
                            "type": "Container",
                            "width": "100%",
                            "height": 50,
                            "background": "#f7fafc",
                            "padding": 15,
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "🔒 Secure Shopping • aipro-skill.com",
                                    "fontSize": 12,
                                    "color": "#718096",
                                    "textAlign": "center"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }

# Simple bright cart APL
def get_simple_bright_cart(cart_items, total):
    """Simple bright cart APL"""
    return {
        "type": "APL",
        "version": "2023.3",
        "mainTemplate": {
            "parameters": ["payload"],
            "items": [
                {
                    "type": "Container",
                    "width": "100vw",
                    "height": "100vh",
                    "background": "#ffffff",
                    "padding": 30,
                    "items": [
                        {
                            "type": "Text",
                            "text": "🛒 Your Cart",
                            "fontSize": 32,
                            "fontWeight": "bold",
                            "color": "#2d3748",
                            "marginBottom": 20
                        },
                        {
                            "type": "Sequence",
                            "height": "60vh",
                            "data": "${payload.cartItems}",
                            "item": {
                                "type": "Container",
                                "background": "#f7fafc",
                                "borderRadius": 15,
                                "padding": 15,
                                "marginBottom": 10,
                                "direction": "row",
                                "items": [
                                    {
                                        "type": "Image",
                                        "source": "${data.image_url}",
                                        "width": 80,
                                        "height": 80,
                                        "scale": "best-fit",
                                        "borderRadius": 10
                                    },
                                    {
                                        "type": "Container",
                                        "paddingLeft": 15,
                                        "grow": 1,
                                        "items": [
                                            {
                                                "type": "Text",
                                                "text": "${data.name}",
                                                "fontSize": 16,
                                                "fontWeight": "bold",
                                                "color": "#2d3748"
                                            },
                                            {
                                                "type": "Text",
                                                "text": "$${data.price}",
                                                "fontSize": 20,
                                                "fontWeight": "bold",
                                                "color": "#48bb78",
                                                "marginTop": 5
                                            }
                                        ]
                                    }
                                ]
                            }
                        },
                        {
                            "type": "Container",
                            "marginTop": 20,
                            "padding": 20,
                            "background": "#f7fafc",
                            "borderRadius": 15,
                            "items": [
                                {
                                    "type": "Container",
                                    "direction": "row",
                                    "justifyContent": "spaceBetween",
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Total:",
                                            "fontSize": 24,
                                            "fontWeight": "bold",
                                            "color": "#2d3748"
                                        },
                                        {
                                            "type": "Text",
                                            "text": "$${payload.cartTotal}",
                                            "fontSize": 32,
                                            "fontWeight": "bold",
                                            "color": "#48bb78"
                                        }
                                    ]
                                },
                                {
                                    "type": "Container",
                                    "marginTop": 15,
                                    "padding": 15,
                                    "background": "#667eea",
                                    "borderRadius": 10,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "💳 Say: Checkout now",
                                            "fontSize": 18,
                                            "fontWeight": "bold",
                                            "color": "#ffffff",
                                            "textAlign": "center"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }

# Simple bright confirmation
def get_simple_bright_confirmation(order_id, total, tracking):
    """Simple bright confirmation APL"""
    return {
        "type": "APL",
        "version": "2023.3",
        "mainTemplate": {
            "parameters": ["payload"],
            "items": [
                {
                    "type": "Container",
                    "width": "100vw",
                    "height": "100vh",
                    "background": "#ffffff",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "items": [
                        {
                            "type": "Container",
                            "padding": 40,
                            "background": "#f7fafc",
                            "borderRadius": 20,
                            "alignItems": "center",
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "✅",
                                    "fontSize": 80,
                                    "marginBottom": 20
                                },
                                {
                                    "type": "Text",
                                    "text": "Order Confirmed!",
                                    "fontSize": 36,
                                    "fontWeight": "bold",
                                    "color": "#48bb78",
                                    "marginBottom": 20
                                },
                                {
                                    "type": "Text",
                                    "text": "Order #${payload.orderId}",
                                    "fontSize": 20,
                                    "color": "#2d3748",
                                    "marginBottom": 30
                                },
                                {
                                    "type": "Text",
                                    "text": "Total: $${payload.orderTotal}",
                                    "fontSize": 24,
                                    "fontWeight": "bold",
                                    "color": "#2d3748",
                                    "marginBottom": 15
                                },
                                {
                                    "type": "Text",
                                    "text": "Tracking: ${payload.trackingNumber}",
                                    "fontSize": 16,
                                    "color": "#718096"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }



