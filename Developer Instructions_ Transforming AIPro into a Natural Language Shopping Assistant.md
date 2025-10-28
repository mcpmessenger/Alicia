# Developer Instructions: Transforming AIPro into a Natural Language Shopping Assistant

**Goal:** Integrate a commerce-focused tool into the AIPro Model Context Protocol (MCP) to enable natural language shopping and affiliate link generation within the existing AWS Lambda and Alexa Skill infrastructure.

**Project Context:** AIPro is an Alexa Skill built on AWS Lambda and DynamoDB, using a multi-provider LLM approach. This guide assumes the developer will use their own LLM API keys (non-BYOK model) and aims to monetize through affiliate revenue and a premium subscription tier.

## 1. Architectural Changes and New Components

The transformation requires the introduction of two main components, both of which will be integrated as "tools" within the MCP framework, allowing the LLM to call them when a shopping intent is detected.

### 1.1. New Components Overview

| Component | Purpose | Location | Dependency |
| :--- | :--- | :--- | :--- |
| **Product Search Tool (`product_search_tool`)** | Executes a product search based on natural language query and returns structured data (name, price, URL, image). | New Python module (e.g., `shopping_tools.py`) | E-commerce API (e.g., Amazon Product Advertising API, or a dedicated scraper service) |
| **Affiliate Link Injector (`affiliate_injector`)** | Takes a product URL and automatically embeds the developer's Amazon Associates Tracking ID or other affiliate IDs. | Integrated within `product_search_tool` or as a utility function. | Developer's Affiliate IDs (stored securely in Lambda Environment Variables or KMS) |
| **User State Manager (Enhanced)** | Stores user's current shopping context (e.g., "I'm looking for a coffee maker"), previous search results, and premium subscription status. | Existing DynamoDB table | Existing DynamoDB connection |

### 1.2. High-Level Request Flow

1.  **User Utterance (Voice):** "Alexa, ask AI Pro to find me a good noise-canceling headphone under $200."
2.  **Alexa Skill Handler (`lambda_function.py`):** Receives the request and passes the query to the LLM Orchestrator.
3.  **LLM Orchestrator (MCP Logic):** The LLM analyzes the query and determines that the `product_search_tool` is the most appropriate action.
4.  **Tool Execution:** The LLM calls the tool with the structured query: `product_search_tool(query="noise-canceling headphones", max_price=200)`.
5.  **Affiliate Injection:** The tool retrieves product data, and the `affiliate_injector` transforms the product URL into a monetized link.
6.  **Response Generation:** The tool returns the structured product data (including the monetized link) to the LLM.
7.  **Final Response:** The LLM synthesizes a voice response (e.g., "I found three options. I've sent the details to your Alexa app.") and the Lambda function sends the voice response and a rich **Alexa Card** (or APL document) containing the visual results to the user.

## 2. Detailed Code Modification Instructions

These instructions focus on modifying the existing `lambda_function.py` and adding the new tool logic.

### 2.1. Tool Logic (`shopping_tools.py`)

Create a new file, `shopping_tools.py`, to house the core commerce logic.

```python
# shopping_tools.py

import os
import requests
import json

# Securely retrieve affiliate ID from environment variables
AMAZON_ASSOCIATES_ID = os.environ.get("AMAZON_ASSOCIATES_ID", "your-default-tracking-id")

def affiliate_injector(url: str, source: str) -> str:
    """
    Injects the appropriate affiliate tracking ID into a product URL.
    This function needs to be customized for each affiliate program.
    """
    if "amazon.com" in url:
        # Simple example: for Amazon, append the tag parameter
        if "?" in url:
            return f"{url}&tag={AMAZON_ASSOCIATES_ID}"
        else:
            return f"{url}?tag={AMAZON_ASSOCIATES_ID}"
    # Add logic for other affiliate networks (e.g., ShareASale, CJ)
    # elif "other-site.com" in url:
    #     return generate_cj_link(url)
    return url

def product_search_tool(query: str, max_price: float = None) -> str:
    """
    Searches for products using an external e-commerce API and returns 
    a JSON string of the results with monetized links.
    
    NOTE: Replace this placeholder with actual API calls (e.g., Amazon PA-API).
    """
    
    # --- Placeholder for actual API call ---
    # In a real scenario, this would call an API like Amazon PA-API, 
    # eBay API, or a dedicated product data provider.
    
    # Mock data for demonstration:
    mock_results = [
        {
            "name": "Sony WH-1000XM5 Noise Cancelling Headphones",
            "price": 398.00,
            "url": "https://www.amazon.com/Sony-WH-1000XM5-Canceling-Headphones-Silver/dp/B09XS6R15N",
            "image_url": "https://example.com/sony_xm5.jpg"
        },
        {
            "name": "Bose QuietComfort Ultra Headphones",
            "price": 429.00,
            "url": "https://www.amazon.com/Bose-QuietComfort-Ultra-Cancelling-Headphones/dp/B0CGH7351Y",
            "image_url": "https://example.com/bose_qc.jpg"
        }
    ]
    
    # 1. Apply price filter (if any)
    if max_price:
        mock_results = [p for p in mock_results if p['price'] <= max_price]

    # 2. Inject affiliate links
    for product in mock_results:
        product['url'] = affiliate_injector(product['url'], 'amazon')
        
    # 3. Return a structured string for the LLM to process
    return json.dumps({
        "status": "success",
        "query": query,
        "results": mock_results
    })

# --- MCP Tool Definition ---
# This is the definition the LLM Orchestrator will use to decide when to call the tool.
tool_definition = {
    "name": "product_search_tool",
    "description": "A tool to search for physical products on e-commerce sites like Amazon and return a list of product names, prices, and affiliate-tracked URLs. Use this for any shopping, product recommendation, or price comparison query.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The natural language query for the product search, e.g., 'best coffee maker' or 'running shoes'."
            },
            "max_price": {
                "type": "number",
                "description": "An optional maximum price limit for the search results."
            }
        },
        "required": ["query"]
    }
}
```

### 2.2. Lambda Handler Integration (`lambda_function.py`)

You will need to modify your main Lambda function to:

1.  Import the new tool.
2.  Add the tool's definition to the list of available tools for the LLM Orchestrator.
3.  Implement a new handler to process the tool's structured output and format it for the Alexa response card.

*   **Step 1: Import Tool**
    Add the following import at the top of `lambda_function.py`:
    ```python
    from shopping_tools import product_search_tool, tool_definition as product_search_tool_definition
    ```

*   **Step 2: Register Tool**
    In the section where you define your list of available tools for the LLM (e.g., `available_tools`), add the new tool definition:
    ```python
    available_tools = [
        # Existing tools (e.g., 'web_search_tool_definition')
        product_search_tool_definition,
    ]
    ```

*   **Step 3: Implement Tool Invocation**
    In the main request handler (where the LLM response is processed), add logic to check if the LLM has requested a tool call to `product_search_tool`.
    ```python
    # Inside your main handler function (e.g., lambda_handler):
    
    # ... existing code to get LLM response ...
    
    if llm_response.tool_call_requested and llm_response.tool_name == "product_search_tool":
        # Extract arguments
        args = llm_response.tool_arguments
        
        # Call the tool function
        tool_output = product_search_tool(**args)
        
        # Send tool output back to the LLM for final synthesis
        final_llm_response = llm_orchestrator.continue_conversation(
            user_input=None, 
            tool_output=tool_output,
            # ... other necessary parameters ...
        )
        
        # Process final_llm_response for voice and visual output
        return self._build_shopping_response(final_llm_response, tool_output)
        
    # ... existing code for standard text response ...
    ```

*   **Step 4: Create Shopping Response Builder**
    Define a new private method `_build_shopping_response` to handle the Alexa response, ensuring the affiliate links and product details are included in the visual card (Display Card or APL).

    ```python
    def _build_shopping_response(self, llm_text_response: str, tool_output_json: str):
        """
        Builds the Alexa response, including the voice output and a visual card 
        with product details and affiliate links.
        """
        import json
        
        # 1. Parse the structured tool output
        tool_data = json.loads(tool_output_json)
        products = tool_data.get('results', [])
        
        # 2. Build the voice response (SSML)
        # The LLM should have synthesized a good voice response, but ensure a fallback.
        speech_text = llm_text_response
        
        # 3. Build the Alexa Display Card (or APL for richer visuals)
        # For simplicity, we use a basic card here. APL is recommended for shopping.
        card_title = f"Shopping Results for: {tool_data.get('query', 'Products')}"
        card_content = "I found the following products:\n\n"
        
        for product in products:
            card_content += f"- {product['name']} (${product['price']:.2f})\n"
            # Crucially, include the monetized URL in the card content
            card_content += f"  Link: {product['url']}\n" 
            
        # 4. Return the final Alexa response object
        return {
            "outputSpeech": {
                "type": "SSML",
                "ssml": f"<speak>{speech_text}</speak>"
            },
            "card": {
                "type": "Simple",
                "title": card_title,
                "content": card_content
            },
            "shouldEndSession": True
        }
    ```


## 3. Alexa Interaction Model and Web Portal Updates

The visual component is crucial for monetization, as affiliate links are most effective when they are clickable and accompanied by rich media (images, price).

### 3.1. Alexa Interaction Model (`alexa-interaction-model.json`)

No new intents are strictly required, as the existing `AMAZON.FallbackIntent` or a general `AskIntent` can capture the natural language shopping query. The intelligence is in the LLM's tool-calling logic.

**Recommendation:** Ensure your sample utterances for your main intent are broad enough to cover shopping queries.

*   **Example Utterance to Add:**
    *   `Ask AI Pro to find me {product_query}`
    *   `Ask AI Pro what is the best {product}`
    *   `Ask AI Pro for a recommendation on {product}`

### 3.2. Web Portal Update (`web_portal.py`)

The Web Portal is the most effective way to present the rich, visual shopping results and ensure high click-through rates on the affiliate links. This is a critical step for maximizing affiliate revenue.

*   **New Endpoint:** Add a new endpoint (e.g., `/shopping-results`) to the web portal application. This endpoint will be the destination for the link you send to the user's Alexa app card.
*   **Data Retrieval:** This endpoint should retrieve the latest shopping results from the user's session data in DynamoDB (which the Lambda function saved).
*   **Visual Display (HTML/CSS):** The HTML/CSS for this page must be updated to display the product results in an attractive, visual format (similar to a search engine results page).

**Example HTML/Jinja Snippet for Product Card:**

```html
{% for product in shopping_results %}
<div class="product-card">
    <img src="{{ product.image_url }}" alt="{{ product.name }}" class="product-image">
    <div class="product-details">
        <h3>{{ product.name }}</h3>
        <p class="product-price">${{ product.price | round(2) }}</p>
        <p class="product-description">
            {{ product.description | truncate(150) }}
        </p>
        <a href="{{ product.url }}" target="_blank" class="affiliate-button">
            Buy Now on Amazon (Affiliate Link)
        </a>
    </div>
</div>
{% endfor %}
```

**Key Requirement:** The `affiliate-button` MUST use the **monetized affiliate URL** generated by the `affiliate_injector` tool.

### 3.3. Alexa Card/APL Integration

In the `_build_shopping_response` function in `lambda_function.py` (Section 2.2, Step 4), you must ensure the Alexa response includes a **Link Account Card** or a **Standard Card** that directs the user to the Web Portal.

**Recommended Approach: Use an Alexa Card with a Deep Link**

Instead of just putting the raw link in the content, use the `Standard` card type to provide a clickable link to your web portal.

```python
# Inside _build_shopping_response:
# ...
# 3. Build the Alexa Display Card (Standard Card recommended)
card_title = f"Shopping Results for: {tool_data.get('query', 'Products')}"
card_content = "I found the following products. View them on your AIPro Web Portal for images and clickable links."
web_portal_link = "YOUR_WEB_PORTAL_URL/shopping-results" # Update with your actual URL

return {
    # ... outputSpeech ...
    "card": {
        "type": "Standard",
        "title": card_title,
        "text": card_content,
        "image": {
            # Optionally, a small logo or a product image
            "smallImageUrl": "https://your-domain.com/logo.png" 
        }
    },
    # ... shouldEndSession ...
}
```

For the best user experience, consider using **Alexa Presentation Language (APL)** [4] to display the product cards directly on screen-enabled devices (Echo Show, Fire TV). This provides the most seamless visual experience.

### 3.1. Alexa Interaction Model (`alexa-interaction-model.json`)

No new intents are strictly required, as the existing `AMAZON.FallbackIntent` or a general `AskIntent` can capture the natural language shopping query. The intelligence is in the LLM's tool-calling logic.

**Recommendation:** Ensure your sample utterances for your main intent are broad enough to cover shopping queries.

*   **Example Utterance to Add:**
    *   `Ask AI Pro to find me {product_query}`
    *   `Ask AI Pro what is the best {product}`
    *   `Ask AI Pro for a recommendation on {product}`

### 3.2. Web Portal Update (`web_portal.py`)

The Web Portal is the most effective way to present the rich, visual shopping results and ensure high click-through rates on the affiliate links.

*   **New Endpoint:** Add a new endpoint (e.g., `/shopping-results`) to the web portal application.
*   **Data Retrieval:** This endpoint should retrieve the latest shopping results from the user's session data in DynamoDB (which the Lambda function saved).
*   **Visual Display:** The HTML/CSS for this page must be updated to display the product results in an attractive, visual format:
    *   Product Image (from `image_url`)
    *   Product Name and Price
    *   A clear, clickable "View Product" button that uses the **monetized affiliate URL**.

## 4. Deployment and Configuration

### 4.1. Environment Variables

Update your AWS Lambda deployment (e.g., in `ai-assistant-infrastructure.yaml` or directly in the AWS Console) to include the new environment variable:

| Variable | Value | Purpose |
| :--- | :--- | :--- |
| `AMAZON_ASSOCIATES_ID` | Your Amazon Associates Tracking ID (e.g., `ai-pro-20`) | Used by the `affiliate_injector` for monetization. |

### 4.2. Dependencies

If you use an external API for product search, you may need to add a new library to your `requirements.txt` (e.g., `requests` for API calls, if not already present).

### 4.3. Final Deployment Steps

1.  **Register as an Amazon Associate:** Enroll in the Amazon Associates program and obtain your tracking ID.
2.  **Update Environment:** Set the `AMAZON_ASSOCIATES_ID` environment variable in your Lambda function.
3.  **Install Dependencies:** Ensure `shopping_tools.py` and any new dependencies are included in your deployment package.
4.  **Redeploy:** Redeploy the updated Lambda function and the Web Portal application.

```bash
# Example deployment commands
# 1. Package the code
zip -r lambda_function.zip lambda_function.py shopping_tools.py requirements.txt # ... other files
# 2. Update Lambda code
aws lambda update-function-code --function-name YOUR_LAMBDA_NAME --zip-file fileb://lambda_function.zip
# 3. Update Web Portal (if separate deployment)
# ...
```

---
### References

[1] mcpmessenger. (2025). *AIPro: AI Assistant Pro - Multi-Provider LLM Alexa Skill*. GitHub.
[2] Amazon Developer. (2024). *Register for Amazon Associates on Alexa*. Alexa Skills Kit. (Note: Direct link inaccessible, but the program is confirmed to exist for skills.)
[3] AWS. (n.d.). *AWS Lambda Environment Variables*. AWS Documentation.
[4] Amazon Developer. (n.d.). *Display Cards and APL for Alexa Skills*. Alexa Skills Kit.

### 4.1. Environment Variables

Update your AWS Lambda deployment (e.g., in `ai-assistant-infrastructure.yaml` or directly in the AWS Console) to include the new environment variable:

| Variable | Value | Purpose |
| :--- | :--- | :--- |
| `AMAZON_ASSOCIATES_ID` | Your Amazon Associates Tracking ID (e.g., `ai-pro-20`) | Used by the `affiliate_injector` for monetization. |

### 4.2. Dependencies

If you use an external API for product search, you may need to add a new library to your `requirements.txt` (e.g., `requests` for API calls, if not already present).

---
### References

[1] mcpmessenger. (2025). *AIPro: AI Assistant Pro - Multi-Provider LLM Alexa Skill*. GitHub.
[2] Amazon Developer. (2024). *Register for Amazon Associates on Alexa*. Alexa Skills Kit. (Note: Direct link inaccessible, but the program is confirmed to exist for skills.)
[3] AWS. (n.d.). *AWS Lambda Environment Variables*. AWS Documentation.
[4] Amazon Developer. (n.d.). *Display Cards and APL for Alexa Skills*. Alexa Skills Kit.
