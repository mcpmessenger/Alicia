"""
Enhanced APL Documents for Beautiful Alexa Webstore
Responsive design for both Echo Show and Echo Spot devices
"""

def get_apl_document_products_enhanced(products, query):
    """
    Beautiful product listing APL with responsive design.
    Works on both large screens (Echo Show) and small screens (Echo Spot).
    """
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
                    "direction": "column",
                    "background": "#ffffff",
                    "items": [
                        # Header with search query
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingTop": 16,
                            "paddingBottom": 16,
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "background": {
                                "type": "LinearGradient",
                                "colorRange": ["#667eea", "#764ba2"],
                                "angle": 135
                            },
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "Search Results",
                                    "fontSize": 18,
                                    "fontWeight": "300",
                                    "color": "rgba(255, 255, 255, 0.8)",
                                    "fontSize": 14
                                },
                                {
                                    "type": "Text",
                                    "text": "${payload.query}",
                                    "fontSize": 28,
                                    "fontWeight": "bold",
                                    "color": "#ffffff",
                                    "marginTop": 4
                                }
                            ]
                        },
                        # Product count indicator
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "paddingTop": 12,
                            "paddingBottom": 12,
                            "background": "#f7fafc",
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "${payload.products.length} products found",
                                    "fontSize": 12,
                                    "color": "#718096",
                                    "fontWeight": "500"
                                }
                            ]
                        },
                        # Product list with scroll
                        {
                            "type": "Sequence",
                            "width": "100%",
                            "height": "1fr",
                            "scrollDirection": "vertical",
                            "data": "${payload.products}",
                            "numbered": False,
                            "items": [
                                {
                                    "type": "Container",
                                    "width": "100%",
                                    "paddingLeft": 16,
                                    "paddingRight": 16,
                                    "paddingTop": 12,
                                    "paddingBottom": 12,
                                    "items": [
                                        {
                                            "type": "Container",
                                            "width": "100%",
                                            "background": "#ffffff",
                                            "borderRadius": 12,
                                            "paddingLeft": 16,
                                            "paddingRight": 16,
                                            "paddingTop": 16,
                                            "paddingBottom": 16,
                                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.08)",
                                            "items": [
                                                # Product image and info row
                                                {
                                                    "type": "Container",
                                                    "direction": "row",
                                                    "items": [
                                                        # Product image
                                                        {
                                                            "type": "Image",
                                                            "source": "${data.image_url}",
                                                            "width": 120,
                                                            "height": 120,
                                                            "scale": "best-fit",
                                                            "borderRadius": 8,
                                                            "boxShadow": "0 2px 6px rgba(0, 0, 0, 0.1)"
                                                        },
                                                        # Product details
                                                        {
                                                            "type": "Container",
                                                            "direction": "column",
                                                            "paddingLeft": 16,
                                                            "grow": 1,
                                                            "items": [
                                                                # Product name
                                                                {
                                                                    "type": "Text",
                                                                    "text": "${data.name}",
                                                                    "fontSize": 16,
                                                                    "fontWeight": "bold",
                                                                    "color": "#2d3748",
                                                                    "maxLines": 2
                                                                },
                                                                # Price and rating row
                                                                {
                                                                    "type": "Container",
                                                                    "direction": "row",
                                                                    "marginTop": 8,
                                                                    "alignItems": "center",
                                                                    "items": [
                                                                        # Price
                                                                        {
                                                                            "type": "Text",
                                                                            "text": "$${data.price}",
                                                                            "fontSize": 20,
                                                                            "fontWeight": "bold",
                                                                            "color": "#48bb78"
                                                                        },
                                                                        # Rating
                                                                        {
                                                                            "type": "Text",
                                                                            "text": "⭐ ${data.rating}",
                                                                            "fontSize": 12,
                                                                            "color": "#f6ad55",
                                                                            "marginLeft": 12
                                                                        }
                                                                    ]
                                                                },
                                                                # Description
                                                                {
                                                                    "type": "Text",
                                                                    "text": "${data.description}",
                                                                    "fontSize": 12,
                                                                    "color": "#718096",
                                                                    "maxLines": 2,
                                                                    "marginTop": 8
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                },
                                                # Action button
                                                {
                                                    "type": "Container",
                                                    "width": "100%",
                                                    "marginTop": 12,
                                                    "paddingTop": 12,
                                                    "borderTopWidth": 1,
                                                    "borderTopColor": "#e2e8f0",
                                                    "items": [
                                                        {
                                                            "type": "Text",
                                                            "text": "Say: Add item ${index+1}",
                                                            "fontSize": 12,
                                                            "color": "#667eea",
                                                            "fontWeight": "bold",
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
                    ]
                }
            ]
        }
    }


def get_apl_document_cart_enhanced(cart):
    """
    Beautiful shopping cart APL with responsive design.
    Shows all cart items with total and checkout prompt.
    """
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
                    "direction": "column",
                    "background": "#ffffff",
                    "items": [
                        # Header
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingTop": 16,
                            "paddingBottom": 16,
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "background": {
                                "type": "LinearGradient",
                                "colorRange": ["#667eea", "#764ba2"],
                                "angle": 135
                            },
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "🛒 Your Shopping Cart",
                                    "fontSize": 28,
                                    "fontWeight": "bold",
                                    "color": "#ffffff"
                                }
                            ]
                        },
                        # Cart items
                        {
                            "type": "Sequence",
                            "width": "100%",
                            "height": "1fr",
                            "scrollDirection": "vertical",
                            "data": "${payload.cartItems}",
                            "numbered": True,
                            "items": [
                                {
                                    "type": "Container",
                                    "width": "100%",
                                    "paddingLeft": 16,
                                    "paddingRight": 16,
                                    "paddingTop": 12,
                                    "paddingBottom": 12,
                                    "items": [
                                        {
                                            "type": "Container",
                                            "width": "100%",
                                            "background": "#f7fafc",
                                            "borderRadius": 8,
                                            "padding": 12,
                                            "items": [
                                                {
                                                    "type": "Container",
                                                    "direction": "row",
                                                    "items": [
                                                        {
                                                            "type": "Text",
                                                            "text": "${index+1}",
                                                            "fontSize": 14,
                                                            "fontWeight": "bold",
                                                            "color": "#667eea",
                                                            "marginRight": 12
                                                        },
                                                        {
                                                            "type": "Container",
                                                            "direction": "column",
                                                            "grow": 1,
                                                            "items": [
                                                                {
                                                                    "type": "Text",
                                                                    "text": "${data.name}",
                                                                    "fontSize": 14,
                                                                    "fontWeight": "bold",
                                                                    "color": "#2d3748"
                                                                },
                                                                {
                                                                    "type": "Text",
                                                                    "text": "$${data.price}",
                                                                    "fontSize": 12,
                                                                    "color": "#48bb78",
                                                                    "marginTop": 4
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        # Cart total and checkout
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingLeft": 16,
                            "paddingRight": 16,
                            "paddingTop": 16,
                            "paddingBottom": 16,
                            "background": "#f7fafc",
                            "items": [
                                {
                                    "type": "Container",
                                    "direction": "row",
                                    "marginBottom": 16,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Total:",
                                            "fontSize": 18,
                                            "fontWeight": "bold",
                                            "color": "#2d3748"
                                        },
                                        {
                                            "type": "Text",
                                            "text": "$${payload.cartTotal}",
                                            "fontSize": 24,
                                            "fontWeight": "bold",
                                            "color": "#48bb78",
                                            "grow": 1,
                                            "textAlign": "right"
                                        }
                                    ]
                                },
                                {
                                    "type": "Container",
                                    "width": "100%",
                                    "background": {
                                        "type": "LinearGradient",
                                        "colorRange": ["#667eea", "#764ba2"],
                                        "angle": 135
                                    },
                                    "borderRadius": 8,
                                    "padding": 12,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Say: Checkout now",
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
            ]
        }
    }


def get_apl_document_checkout_enhanced(order):
    """
    Beautiful order confirmation APL.
    Shows order details and next steps.
    """
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
                    "direction": "column",
                    "background": "#ffffff",
                    "items": [
                        # Success header
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingTop": 24,
                            "paddingBottom": 24,
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "background": {
                                "type": "LinearGradient",
                                "colorRange": ["#48bb78", "#38a169"],
                                "angle": 135
                            },
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "✓ Order Confirmed!",
                                    "fontSize": 28,
                                    "fontWeight": "bold",
                                    "color": "#ffffff",
                                    "textAlign": "center"
                                }
                            ]
                        },
                        # Order details
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "paddingTop": 24,
                            "paddingBottom": 24,
                            "items": [
                                # Order number
                                {
                                    "type": "Container",
                                    "marginBottom": 20,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Order Number",
                                            "fontSize": 12,
                                            "color": "#718096",
                                            "fontWeight": "500"
                                        },
                                        {
                                            "type": "Text",
                                            "text": "${payload.order_id}",
                                            "fontSize": 20,
                                            "fontWeight": "bold",
                                            "color": "#2d3748",
                                            "marginTop": 4

                                        }
                                    ]
                                },
                                # Total amount
                                {
                                    "type": "Container",
                                    "marginBottom": 20,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Total Amount",
                                            "fontSize": 12,
                                            "color": "#718096",
                                            "fontWeight": "500"
                                        },
                                        {
                                            "type": "Text",
                                            "text": "$${payload.total}",
                                            "fontSize": 28,
                                            "fontWeight": "bold",
                                            "color": "#48bb78",
                                            "marginTop": 4
                                        }
                                    ]
                                },
                                # Estimated delivery
                                {
                                    "type": "Container",
                                    "marginBottom": 20,
                                    "items": [
                                        {
                                            "type": "Text",
                                            "text": "Estimated Delivery",
                                            "fontSize": 12,
                                            "color": "#718096",
                                            "fontWeight": "500"
                                        },
                                        {
                                            "type": "Text",
                                            "text": "${payload.estimated_delivery}",
                                            "fontSize": 16,
                                            "color": "#2d3748",
                                            "marginTop": 4
                                        }
                                    ]
                                }
                            ]
                        },
                        # Next steps
                        {
                            "type": "Container",
                            "width": "100%",
                            "paddingLeft": 20,
                            "paddingRight": 20,
                            "paddingTop": 16,
                            "paddingBottom": 16,
                            "background": "#f7fafc",
                            "items": [
                                {
                                    "type": "Text",
                                    "text": "Next Steps",
                                    "fontSize": 14,
                                    "fontWeight": "bold",
                                    "color": "#2d3748",
                                    "marginBottom": 12
                                },
                                {
                                    "type": "Text",
                                    "text": "Check your Alexa app for order details, tracking information, and delivery updates.",
                                    "fontSize": 12,
                                    "color": "#718096",
                                    "lineHeight": 1.6
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
