# Twitter/X Scraper with Sentiment Analysis
# This script scrapes tweets based on keywords, analyzes sentiment using Groq API (Llama model),
# and stores results in MongoDB database

# Import required libraries
import time                                          # For adding delays between operations
import json                                          # For handling JSON data (cookies)
import re                                            # For regular expressions (text cleaning)
from selenium import webdriver                       # Main web automation library
from selenium.webdriver.chrome.options import Options # Chrome browser configuration
from selenium.webdriver.chrome.service import Service # Chrome driver service management
from selenium.webdriver.common.by import By         # Element location methods
from mongodb_handler import insert_or_update_tweet   # Custom function to save tweets to MongoDB
from llama_sentiment import classify_sentiment       # Custom function using Groq API for sentiment analysis

def scrape_tweets(keyword, cookie_path="twitter_cookies.json", headless=True, max_tweets=20):
    """
    Main function to scrape tweets from Twitter/X based on keyword search.
    
    Args:
        keyword (str): Search term to find tweets about (e.g., "climate change", "iPhone")
        cookie_path (str): Path to saved Twitter cookies file for authentication
        headless (bool): Whether to run Chrome in headless mode (invisible browser)
        max_tweets (int): Maximum number of tweets to scrape per session
        
    Returns:
        list: List of dictionaries containing tweet data with sentiment analysis
    """
    
    # Configure Chrome browser options for web scraping
    options = Options()
    
    # Run browser in headless mode (invisible) if specified
    if headless:
        options.add_argument("--headless")
    
    # Add stealth options to avoid bot detection
    options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation signals
    options.add_argument("--disable-notifications")                        # Block popup notifications
    options.add_argument("--disable-infobars")                            # Remove automation info bars
    options.add_argument("--disable-extensions")                          # Disable browser extensions
    options.add_argument("--disable-gpu")                                 # Disable GPU acceleration
    options.add_argument("--no-sandbox")                                  # Security setting for some systems
    
    # Initialize Chrome WebDriver with error handling
    try:
        # Try to use local chromedriver.exe first
        service = Service(executable_path="./chromedriver.exe")
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        # If local driver fails, use system-installed driver
        print(f"Error with specified chromedriver path: {e}")
        print("Falling back to automatic webdriver detection...")
        driver = webdriver.Chrome(options=options)
    
    # Navigate to Twitter/X homepage first
    print("Loading Twitter/X homepage...")
    driver.get("https://x.com")
    time.sleep(6)  # Wait for page to fully load
    
    # Load and apply saved cookies for authentication
    try:
        print(f"Loading cookies from {cookie_path}...")
        with open(cookie_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)  # Parse JSON cookie file
            
            # Process each cookie
            for cookie in cookies:
                # Remove problematic cookie attributes that cause Selenium errors
                cookie.pop("sameSite", None) if "sameSite" in cookie else None
                cookie.pop("storeId", None) if "storeId" in cookie else None
                cookie.pop("expiry", None) if "expiry" in cookie else None
                
                try:
                    driver.add_cookie(cookie)  # Add cookie to browser session
                except Exception as cookie_error:
                    print(f"Cookie error (skipping): {cookie_error}")
                    
    except Exception as cookie_file_error:
        print(f"Error loading cookies from {cookie_path}: {cookie_file_error}")
        print("Continuing without cookies (may have limited access)...")
    
    # Navigate to search results page with the specified keyword
    search_url = f"https://x.com/search?q={keyword}&src=typed_query&f=live"
    print(f"Navigating to search results: {search_url}")
    driver.get(search_url)
    time.sleep(5)  # Wait for search results to load
    
    # Scroll down multiple times to load more tweets (Twitter uses infinite scroll)
    print("Scrolling to load more tweets...")
    for scroll_count in range(5):  # Scroll 5 times
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to bottom
        time.sleep(3)  # Wait for new content to load
        print(f"Scroll {scroll_count + 1}/5 completed")
    
    # Find all tweet elements on the page using XPath selector
    tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    print(f"Found {len(tweets)} tweet elements on page")
    
    # Initialize data collection variables
    scraped_data = []  # List to store all processed tweet data
    counter = 0        # Counter to track processed tweets
    
    # Process each tweet element found on the page
    print("Starting tweet processing...")
    for tweet in tweets:
        # Stop if we've reached the maximum tweet limit
        if counter >= max_tweets:
            print(f"Reached maximum limit of {max_tweets} tweets")
            break
        
        try:
            # Extract the main text content of the tweet
            text_elem = tweet.find_element(By.XPATH, './/div[@lang]')  # Find div with language attribute
            text = text_elem.text  # Get the tweet text
            
            # Extract username with error handling
            try:
                username_elem = tweet.find_element(By.XPATH, './/div[@data-testid="User-Name"]')
                username = username_elem.text.split('\n')[0]  # Get first line (actual username)
            except:
                username = "Unknown"  # Default if username extraction fails
            
            # Extract hashtags from tweet text using regular expressions
            hashtags = re.findall(r"#\w+", text)  # Find all words starting with #
            
            # Clean the text by removing URLs, mentions (@), and hashtags (#)
            clean_text = re.sub(r"http\S+|@\w+|#\w+", "", text).strip()
            
            # Skip tweets with empty text after cleaning
            if not clean_text:
                print("Skipping tweet with empty content after cleaning")
                continue
            
            # Analyze sentiment using Groq API (Llama model)
            print(f"Analyzing sentiment for: {clean_text[:30]}...")
            sentiment = classify_sentiment(clean_text)  # Call custom sentiment analysis function
            
            # Create structured data dictionary for the tweet
            tweet_data = {
                "username": username,                                    # Twitter username
                "text": text,                                           # Original tweet text
                "hashtags": hashtags,                                   # List of hashtags found
                "clean_text": clean_text,                              # Cleaned text for analysis
                "sentiment": sentiment,                                 # Sentiment classification (positive/negative/neutral)
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),       # Current timestamp
                "keyword": keyword                                      # Search keyword used
            }
            
            # Save tweet data to MongoDB database
            inserted_id = insert_or_update_tweet(tweet_data)
            print(f"[✓] Tweet {counter + 1}: {clean_text[:50]}... | Sentiment: {sentiment}")
            
            # Add processed tweet to results list
            scraped_data.append(tweet_data)
            counter += 1  # Increment processed tweet counter
            
        except Exception as processing_error:
            # Log errors but continue processing other tweets
            print(f"[!] Error processing tweet {counter + 1}: {processing_error}")
            continue
    
    # Clean up: close the browser
    driver.quit()
    print(f"[✅] Scraping session complete!")
    print(f"Successfully processed {len(scraped_data)} tweets for keyword: '{keyword}'")
    
    # Return the collected and processed tweet data
    return scraped_data