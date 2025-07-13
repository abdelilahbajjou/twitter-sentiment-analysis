# Import necessary libraries for environment variables, JSON handling, and HTTP requests
import os
import json
import requests

# Retrieve Groq API key from environment variable or use hardcoded fallback
# Best practice: Use environment variables to keep API keys secure
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_api_key_here")

def classify_sentiment(text: str) -> str:
    """
    Sends text to Groq API for sentiment classification using Llama3 model.
    
    Args:
        text (str): The input text to analyze for sentiment
        
    Returns:
        str: One of three sentiment classifications: 'positive', 'negative', or 'neutral'
    """
    
    # Define the Groq API endpoint for chat completions
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Set up HTTP headers with authorization and content type
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",  # Bearer token authentication
        "Content-Type": "application/json"          # Specify JSON payload format
    }
    
    # Create a structured prompt for sentiment analysis
    # This prompt instructs the AI to respond with only one specific word
    prompt = f"""
    Analyze the sentiment of the following tweet. 
    Respond with only one word: 'positive', 'negative', or 'neutral'.
    
    Tweet: {text}
    """
    
    # Construct the API request payload
    payload = {
        "model": "llama3-8b-8192",  # Specify Llama3 model with 8B parameters and 8192 context length
        "messages": [
            # System message defines the AI's role and behavior
            {"role": "system", "content": "You are a sentiment analysis assistant that classifies text as positive, negative, or neutral."},
            # User message contains the actual analysis request
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,  # Low temperature (0.0-1.0) for more consistent, deterministic results
        "max_tokens": 10     # Limit response length since we only need a single word
    }
    
    # Attempt to make API request with error handling
    try:
        # Send POST request to Groq API
        response = requests.post(url, json=payload, headers=headers)
        
        # Raise an exception if the HTTP request returned an error status
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Extract the AI's response text from the API response structure
        response_text = data["choices"][0]["message"]["content"].strip().lower()
        
        # Normalize the response to ensure it matches one of our expected values
        # This handles cases where the AI might return variations like "The sentiment is positive"
        if "positive" in response_text:
            return "positive"
        elif "negative" in response_text:
            return "negative"
        else:
            # Default to neutral if response doesn't clearly indicate positive or negative
            return "neutral"
            
    except Exception as e:
        # Handle any errors (network issues, API errors, parsing errors, etc.)
        print(f"[!] Groq API error: {e}")
        # Return neutral as a safe fallback when analysis fails
        return "neutral"