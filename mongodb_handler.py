# MongoDB Handler for Twitter Sentiment Analysis Project
# This module handles all database operations for storing and retrieving tweet data
# Uses MongoDB as the database backend for scalable data storage

# Import the MongoDB Python driver (pymongo)
from pymongo import MongoClient

# Establish connection to MongoDB server
# MongoDB runs on localhost (your computer) on default port 27017
client = MongoClient("mongodb://localhost:27017/")

# Select or create the database named "twitter_db"
# If the database doesn't exist, MongoDB will create it automatically
db = client["twitter_db"]

# Select or create the collection named "tweets" within the database
# Collections in MongoDB are like tables in SQL databases
collection = db["tweets"]

def insert_tweet(tweet):
    """
    Insert a new tweet document into the MongoDB collection.
    
    This is a simple insert function that adds the tweet directly to the database.
    WARNING: This function can create duplicates if the same tweet is inserted multiple times.
    
    Args:
        tweet (dict): Dictionary containing tweet data (text, username, sentiment, etc.)
        
    Returns:
        ObjectId: The unique identifier MongoDB assigns to the inserted document
    """
    # Insert the tweet dictionary as a new document and return its unique ID
    return collection.insert_one(tweet).inserted_id

def insert_or_update_tweet(tweet):
    """
    Insert a tweet or update it if the same content already exists in the database.
    This is the PREFERRED method as it prevents duplicate tweets.
    
    How it works:
    1. Search for existing tweet with the same clean_text
    2. If found: update the existing document with new data
    3. If not found: insert as a new document
    
    Args:
        tweet (dict): Dictionary containing tweet data with all fields
        
    Returns:
        ObjectId or str: New document ID if inserted, "updated" if existing document was modified
    """
    # Use MongoDB's update_one method with upsert=True for smart insert/update
    result = collection.update_one(
        {"clean_text": tweet["clean_text"]},  # Search condition: find tweet with matching clean_text
        {"$set": tweet},                      # Update operation: replace/set all fields with new tweet data
        upsert=True                          # If no matching document found, insert as new document
    )
    
    # Check if a new document was created (upserted) or existing one was updated
    if result.upserted_id:
        # New document was inserted
        return result.upserted_id
    else:
        # Existing document was updated
        return "updated"

def clear_tweets():
    """
    Delete ALL tweet documents from the collection.
    
    WARNING: This permanently removes all stored tweets from the database.
    Use this function carefully - typically only for testing or cleanup.
    
    Returns:
        None
    """
    # Delete all documents in the collection (empty filter {} matches all documents)
    collection.delete_many({})
    print("All tweets have been deleted from the database.")

def get_all_tweets():
    """
    Retrieve all tweet documents from the database.
    
    This function returns every tweet that has been stored in the collection.
    Be careful with large datasets as this loads everything into memory.
    
    Returns:
        list: List of dictionaries, each representing a tweet document
    """
    # Find all documents (empty filter {}) and convert cursor to list
    return list(collection.find({}))

def get_tweets_by_sentiment(sentiment):
    """
    Retrieve only tweets that match a specific sentiment classification.
    
    This is useful for analyzing specific sentiment categories or creating reports.
    
    Args:
        sentiment (str): The sentiment to filter by ("positive", "negative", or "neutral")
        
    Returns:
        list: List of tweet dictionaries that match the specified sentiment
        
    Example:
        positive_tweets = get_tweets_by_sentiment("positive")
        negative_tweets = get_tweets_by_sentiment("negative")
    """
    # Find documents where the sentiment field matches the specified value
    return list(collection.find({"sentiment": sentiment}))

def get_tweet_stats():
    """
    Calculate and return statistics about the tweets stored in the database.
    
    This function provides a quick overview of your data, including:
    - Total number of tweets
    - Count of positive tweets
    - Count of neutral tweets  
    - Count of negative tweets
    
    Perfect for creating dashboards, reports, or monitoring data quality.
    
    Returns:
        dict: Dictionary containing count statistics for each sentiment category
        
    Example return value:
        {
            "total": 150,
            "positive": 65,
            "neutral": 42,
            "negative": 43
        }
    """
    # Count total documents in the collection
    total = collection.count_documents({})
    
    # Count documents for each sentiment category
    positive = collection.count_documents({"sentiment": "positive"})
    neutral = collection.count_documents({"sentiment": "neutral"})
    negative = collection.count_documents({"sentiment": "negative"})
    
    # Return statistics as a structured dictionary
    return {
        "total": total,
        "positive": positive,
        "neutral": neutral,
        "negative": negative
    }

def get_tweets_by_keyword(keyword):
    """
    Retrieve tweets that were scraped using a specific keyword.
    
    This function helps you analyze tweets by the search term that was used to find them.
    
    Args:
        keyword (str): The keyword to filter by
        
    Returns:
        list: List of tweet dictionaries that match the specified keyword
    """
    # Find documents where the keyword field matches the specified value
    return list(collection.find({"keyword": keyword}))

def get_recent_tweets(limit=10):
    """
    Retrieve the most recently added tweets from the database.
    
    Args:
        limit (int): Maximum number of recent tweets to return (default: 10)
        
    Returns:
        list: List of the most recent tweet dictionaries, sorted by timestamp
    """
    # Find all documents, sort by timestamp in descending order, limit results
    return list(collection.find({}).sort("timestamp", -1).limit(limit))

# Example usage functions for testing the database operations
def test_database_operations():
    """
    Test function to demonstrate how to use the database handler functions.
    This is helpful for debugging and understanding the data flow.
    """
    print("=== Database Operations Test ===")
    
    # Get current statistics
    stats = get_tweet_stats()
    print(f"Current database stats: {stats}")
    
    # Get some recent tweets
    recent = get_recent_tweets(5)
    print(f"Found {len(recent)} recent tweets")
    
    # Get tweets by sentiment
    positive_tweets = get_tweets_by_sentiment("positive")
    print(f"Found {len(positive_tweets)} positive tweets")
    
    return stats

# Database connection test
def test_connection():
    """
    Test if the MongoDB connection is working properly.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Try to get server information
        client.server_info()
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False