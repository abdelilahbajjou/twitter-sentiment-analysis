import threading
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from twitter_scraper import scrape_tweets
from mongodb_handler import insert_or_update_tweet, clear_tweets, get_all_tweets
from llama_sentiment import classify_sentiment
from collections import Counter
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class TweetAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tweet Sentiment Analyzer")
        self.root.geometry("900x700")
        
        # Keyword input frame
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Enter search keyword:").pack(side=tk.LEFT)
        self.keyword_entry = tk.Entry(input_frame, width=30)
        self.keyword_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        
        self.start_button = tk.Button(btn_frame, text="Start Scraping", command=self.start_thread)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.view_button = tk.Button(btn_frame, text="View Results", command=self.view_results)
        self.view_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(btn_frame, text="Clear DB", command=self.clear_database)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Add the Show Graphs button
        self.graph_button = tk.Button(btn_frame, text="Show Graphs", command=self.show_graphs)
        self.graph_button.pack(side=tk.LEFT, padx=5)
        
        # Status area
        tk.Label(root, text="Status:").pack(anchor=tk.W, padx=10)
        self.status_text = scrolledtext.ScrolledText(root, height=3)
        self.status_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Tab 1: Tweet results
        self.tweets_tab = tk.Frame(self.notebook)
        self.notebook.add(self.tweets_tab, text="Tweets")
        
        self.results_text = scrolledtext.ScrolledText(self.tweets_tab, height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Tab 2: Analytics
        self.analytics_tab = tk.Frame(self.notebook)
        self.notebook.add(self.analytics_tab, text="Analytics")
        
        # Create frames for different analytics sections
        self.create_analytics_frames()
        
        # Tab 3: Graphs
        self.graphs_tab = tk.Frame(self.notebook)
        self.notebook.add(self.graphs_tab, text="Graphs")
        
        # Create a container for graphs
        self.graphs_container = tk.Frame(self.graphs_tab)
        self.graphs_container.pack(fill=tk.BOTH, expand=True)
        
        # Statistics frame at bottom
        stats_frame = tk.Frame(root)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.positive_count = tk.StringVar(value="Positive: 0")
        self.neutral_count = tk.StringVar(value="Neutral: 0")
        self.negative_count = tk.StringVar(value="Negative: 0")
        
        tk.Label(stats_frame, textvariable=self.positive_count, fg="green").pack(side=tk.LEFT, padx=10)
        tk.Label(stats_frame, textvariable=self.neutral_count, fg="blue").pack(side=tk.LEFT, padx=10)
        tk.Label(stats_frame, textvariable=self.negative_count, fg="red").pack(side=tk.LEFT, padx=10)
    
    def create_analytics_frames(self):
        # Create a frame for the analytics tab with a grid layout
        analytics_container = tk.Frame(self.analytics_tab)
        analytics_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top hashtags frame
        hashtag_frame = tk.LabelFrame(analytics_container, text="Top Hashtags")
        hashtag_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.hashtags_text = scrolledtext.ScrolledText(hashtag_frame, height=8, width=30)
        self.hashtags_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frequent words frame
        words_frame = tk.LabelFrame(analytics_container, text="Frequent Words")
        words_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.words_text = scrolledtext.ScrolledText(words_frame, height=8, width=30)
        self.words_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Best tweets frame
        best_frame = tk.LabelFrame(analytics_container, text="Best Tweets")
        best_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.best_text = scrolledtext.ScrolledText(best_frame, height=8, width=30)
        self.best_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Worst tweets frame
        worst_frame = tk.LabelFrame(analytics_container, text="Worst Tweets")
        worst_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        self.worst_text = scrolledtext.ScrolledText(worst_frame, height=8, width=30)
        self.worst_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid weights
        analytics_container.grid_columnconfigure(0, weight=1)
        analytics_container.grid_columnconfigure(1, weight=1)
        analytics_container.grid_rowconfigure(0, weight=1)
        analytics_container.grid_rowconfigure(1, weight=1)
        
    def log_status(self, message):
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        
    def worker(self, keyword):
        self.log_status(f"Scraping tweets for keyword: '{keyword}'...")
        
        try:
            # Clear existing tweets before scraping new ones
            clear_tweets()
            self.log_status("Cleared existing tweets from database.")
            
            # Scrape tweets with the keyword
            tweets = scrape_tweets(keyword)
            
            if not tweets:
                self.log_status("No tweets found. Try a different keyword.")
                return
                
            self.log_status(f"Found {len(tweets)} tweets. Processing sentiment...")
            
            for tweet in tweets:
                # The sentiment is already analyzed in the scraper
                self.log_status(f"Tweet: '{tweet['clean_text'][:30]}...' - {tweet['sentiment']}")
            
            self.log_status("Scraping and analysis complete.")
            self.update_stats()
            self.update_analytics()
            
            # Switch to the analytics tab to show results
            self.notebook.select(1)  # Index 1 is the analytics tab
            
        except Exception as e:
            self.log_status(f"Error during scraping: {str(e)}")
    
    def start_thread(self):
        keyword = self.keyword_entry.get()
        if keyword.strip() == "":
            self.log_status("Please enter a search keyword.")
            return
        
        # Disable the button while processing
        self.start_button.config(state=tk.DISABLED)
        
        # Start the worker in a separate thread
        thread = threading.Thread(target=self.worker, args=(keyword,), daemon=True)
        thread.start()
        
        # Check if the thread is still running
        def check_thread():
            if thread.is_alive():
                self.root.after(100, check_thread)
            else:
                self.start_button.config(state=tk.NORMAL)
                
        self.root.after(100, check_thread)
    
    def view_results(self):
        tweets = get_all_tweets()
        
        self.results_text.delete(1.0, tk.END)
        
        if not tweets:
            self.results_text.insert(tk.END, "No tweets found in the database.")
            return
            
        for i, tweet in enumerate(tweets, 1):
            sentiment = tweet.get('sentiment', 'unknown')
            sentiment_color = {
                'positive': 'green',
                'neutral': 'blue',
                'negative': 'red'
            }.get(sentiment, 'black')
            
            self.results_text.insert(tk.END, f"{i}. [{sentiment.upper()}] {tweet['clean_text']}\n\n")
            
            # Need to get the line number positions to apply the tag
            last_line_start = f"{i}.0"
            last_line_end = f"{i}.{len(sentiment) + 2}" # +2 for [ ]
            
            # Create a tag for this sentiment if it doesn't exist
            tag_name = f"sentiment_{sentiment}"
            if tag_name not in self.results_text.tag_names():
                self.results_text.tag_configure(tag_name, foreground=sentiment_color)
                
            # Apply the tag to the sentiment part
            self.results_text.tag_add(tag_name, last_line_start, last_line_end)
        
        self.update_stats()
        self.update_analytics()
        
        # Switch to the tweets tab
        self.notebook.select(0)  # Index 0 is the tweets tab
    
    def clear_database(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all tweets from the database?"):
            clear_tweets()
            self.log_status("Database cleared.")
            self.results_text.delete(1.0, tk.END)
            
            # Clear analytics as well
            self.hashtags_text.delete(1.0, tk.END)
            self.words_text.delete(1.0, tk.END)
            self.best_text.delete(1.0, tk.END)
            self.worst_text.delete(1.0, tk.END)
            
            # Clear any graphs
            for widget in self.graphs_container.winfo_children():
                widget.destroy()
                
            self.update_stats()
    
    def update_stats(self):
        tweets = get_all_tweets()
        
        positive = sum(1 for t in tweets if t.get('sentiment') == 'positive')
        neutral = sum(1 for t in tweets if t.get('sentiment') == 'neutral')
        negative = sum(1 for t in tweets if t.get('sentiment') == 'negative')
        
        self.positive_count.set(f"Positive: {positive}")
        self.neutral_count.set(f"Neutral: {neutral}")
        self.negative_count.set(f"Negative: {negative}")
    
    def update_analytics(self):
        tweets = get_all_tweets()
        
        if not tweets:
            return
            
        # Process hashtags
        self.analyze_hashtags(tweets)
        
        # Process frequent words
        self.analyze_frequent_words(tweets)
        
        # Process best/worst tweets
        self.analyze_best_worst_tweets(tweets)
    
    def analyze_hashtags(self, tweets):
        # Extract all hashtags from all tweets
        all_hashtags = []
        for tweet in tweets:
            all_hashtags.extend(tweet.get('hashtags', []))
        
        # Count hashtags
        hashtag_counts = Counter(all_hashtags)
        
        # Display top hashtags
        self.hashtags_text.delete(1.0, tk.END)
        
        if not hashtag_counts:
            self.hashtags_text.insert(tk.END, "No hashtags found")
            return
            
        # Show top 10 hashtags with counts
        self.hashtags_text.insert(tk.END, "Top hashtags:\n\n")
        for hashtag, count in hashtag_counts.most_common(10):
            self.hashtags_text.insert(tk.END, f"{hashtag}: {count}\n")
    
    def analyze_frequent_words(self, tweets):
        # Combine all cleaned tweet text
        all_text = " ".join([tweet.get('clean_text', '') for tweet in tweets])
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', all_text.lower())
        
        # Filter out common words (stopwords)
        stopwords = {"a", "an", "the", "and", "or", "but", "is", "are", "was", "were", 
                     "be", "been", "being", "in", "on", "at", "to", "for", "with", 
                     "by", "about", "against", "between", "into", "through", "during",
                     "before", "after", "above", "below", "from", "up", "down", "of", 
                     "off", "over", "under", "again", "further", "then", "once", "here",
                     "there", "when", "where", "why", "how", "all", "any", "both", "each",
                     "few", "more", "most", "other", "some", "such", "no", "nor", "not",
                     "only", "own", "same", "so", "than", "too", "very", "s", "t", "can",
                     "will", "just", "don", "should", "now", "i", "me", "my", "myself",
                     "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
                     "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
                     "herself", "it", "its", "itself", "they", "them", "their", "theirs",
                     "themselves", "what", "which", "who", "whom", "this", "that", "these",
                     "those", "am", "is", "are", "was", "were", "be", "been", "being", "have",
                     "has", "had", "having", "do", "does", "did", "doing", "would", "should",
                     "could", "ought", "i'm", "you're", "he's", "she's", "it's", "we're",
                     "they're", "i've", "you've", "we've", "they've", "i'd", "you'd", "he'd",
                     "she'd", "we'd", "they'd", "i'll", "you'll", "he'll", "she'll", "we'll",
                     "they'll", "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't",
                     "hadn't", "doesn't", "don't", "didn't", "won't", "wouldn't", "shan't",
                     "shouldn't", "can't", "cannot", "couldn't", "mustn't", "let's", "that's",
                     "who's", "what's", "here's", "there's", "when's", "where's", "why's",
                     "how's", "yeah", "u", "ur", "r", "n", "im", "m", "rt"}
        
        filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
        
        # Count words
        word_counts = Counter(filtered_words)
        
        # Display top words
        self.words_text.delete(1.0, tk.END)
        
        if not word_counts:
            self.words_text.insert(tk.END, "No significant words found")
            return
            
        # Show top 15 words with counts
        self.words_text.insert(tk.END, "Most frequent words:\n\n")
        for word, count in word_counts.most_common(15):
            self.words_text.insert(tk.END, f"{word}: {count}\n")
    
    def analyze_best_worst_tweets(self, tweets):
        # Clear existing text
        self.best_text.delete(1.0, tk.END)
        self.worst_text.delete(1.0, tk.END)
        
        # Find positive tweets
        positive_tweets = [t for t in tweets if t.get('sentiment') == 'positive']
        # Find negative tweets
        negative_tweets = [t for t in tweets if t.get('sentiment') == 'negative']
        
        # Display best tweets (up to 5)
        if positive_tweets:
            for i, tweet in enumerate(positive_tweets[:5], 1):
                self.best_text.insert(tk.END, f"{i}. {tweet['clean_text'][:100]}...\n\n")
        else:
            self.best_text.insert(tk.END, "No positive tweets found")
        
        # Display worst tweets (up to 5)
        if negative_tweets:
            for i, tweet in enumerate(negative_tweets[:5], 1):
                self.worst_text.insert(tk.END, f"{i}. {tweet['clean_text'][:100]}...\n\n")
        else:
            self.worst_text.insert(tk.END, "No negative tweets found")
    
    def show_graphs(self):
        tweets = get_all_tweets()
        
        if not tweets:
            messagebox.showinfo("No Data", "There are no tweets to visualize. Please scrape some tweets first.")
            return
        
        # Clear any existing graphs
        for widget in self.graphs_container.winfo_children():
            widget.destroy()
        
        # Create a notebook for different graph types
        graph_notebook = ttk.Notebook(self.graphs_container)
        graph_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs for different graph types
        self.create_sentiment_distribution_chart(graph_notebook, tweets)
        # Removed the hashtags chart because the counts are all 1
        self.create_top_words_chart(graph_notebook, tweets)
        self.create_sentiment_trend_chart(graph_notebook, tweets)
        
        # Switch to the graphs tab
        self.notebook.select(2)  # Index 2 is the graphs tab
    
    def create_sentiment_distribution_chart(self, parent, tweets):
        frame = ttk.Frame(parent)
        parent.add(frame, text="Sentiment Distribution")
        
        # Count sentiments
        positive = sum(1 for t in tweets if t.get('sentiment') == 'positive')
        neutral = sum(1 for t in tweets if t.get('sentiment') == 'neutral')
        negative = sum(1 for t in tweets if t.get('sentiment') == 'negative')
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)
        
        # Create pie chart
        labels = ['Positive', 'Neutral', 'Negative']
        sizes = [positive, neutral, negative]
        colors = ['green', 'blue', 'red']
        explode = (0.1, 0, 0)  # explode the 1st slice (Positive)
        
        ax.pie(sizes, explode=explode, labels=labels, colors=colors, 
               autopct='%1.1f%%', shadow=True, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        ax.set_title('Tweet Sentiment Distribution')
        
        # Embed the chart in the frame
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # The create_top_hashtags_chart method is still present in the code but no longer called
    def create_top_hashtags_chart(self, parent, tweets):
        # Extract all hashtags
        all_hashtags = []
        for tweet in tweets:
            all_hashtags.extend(tweet.get('hashtags', []))
        
        # Count hashtags
        hashtag_counts = Counter(all_hashtags)
        
        if not hashtag_counts:
            # Skip creating this chart if no hashtags
            return
        
        frame = ttk.Frame(parent)
        parent.add(frame, text="Top Hashtags")
        
        # Get top 10 hashtags
        top_hashtags = hashtag_counts.most_common(10)
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)
        
        # Create horizontal bar chart
        hashtags = [h[0] for h in top_hashtags]
        counts = [h[1] for h in top_hashtags]
        
        # Reverse lists to have highest value at the top
        hashtags.reverse()
        counts.reverse()
        
        ax.barh(hashtags, counts, color='skyblue')
        ax.set_xlabel('Count')
        ax.set_ylabel('Hashtag')
        ax.set_title('Top Hashtags')
        
        # Add count labels to the bars
        for i, v in enumerate(counts):
            ax.text(v + 0.1, i, str(v), va='center')
        
        # Embed the chart in the frame
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_top_words_chart(self, parent, tweets):
        # Combine all cleaned tweet text
        all_text = " ".join([tweet.get('clean_text', '') for tweet in tweets])
        
        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', all_text.lower())
        
        # Filter out common words (stopwords)
        stopwords = {"a", "an", "the", "and", "or", "but", "is", "are", "was", "were", 
                     "be", "been", "being", "in", "on", "at", "to", "for", "with", 
                     "by", "about", "against", "between", "into", "through", "during",
                     "before", "after", "above", "below", "from", "up", "down", "of", 
                     "off", "over", "under", "again", "further", "then", "once", "here",
                     "there", "when", "where", "why", "how", "all", "any", "both", "each",
                     "few", "more", "most", "other", "some", "such", "no", "nor", "not",
                     "only", "own", "same", "so", "than", "too", "very", "s", "t", "can",
                     "will", "just", "don", "should", "now", "i", "me", "my", "myself",
                     "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
                     "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
                     "herself", "it", "its", "itself", "they", "them", "their", "theirs",
                     "themselves", "what", "which", "who", "whom", "this", "that", "these",
                     "those", "am", "is", "are", "was", "were", "be", "been", "being", "have",
                     "has", "had", "having", "do", "does", "did", "doing", "would", "should",
                     "could", "ought", "i'm", "you're", "he's", "she's", "it's", "we're",
                     "they're", "i've", "you've", "we've", "they've", "i'd", "you'd", "he'd",
                     "she'd", "we'd", "they'd", "i'll", "you'll", "he'll", "she'll", "we'll",
                     "they'll", "isn't", "aren't", "wasn't", "weren't", "hasn't", "haven't",
                     "hadn't", "doesn't", "don't", "didn't", "won't", "wouldn't", "shan't",
                     "shouldn't", "can't", "cannot", "couldn't", "mustn't", "let's", "that's",
                     "who's", "what's", "here's", "there's", "when's", "where's", "why's",
                     "how's", "yeah", "u", "ur", "r", "n", "im", "m", "rt"}
        
        filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
        
        # Count words
        word_counts = Counter(filtered_words)
        
        if not word_counts:
            # Skip creating this chart if no significant words
            return
        
        frame = ttk.Frame(parent)
        parent.add(frame, text="Top Words")
        
        # Get top 15 words
        top_words = word_counts.most_common(15)
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)
        
        # Create horizontal bar chart
        words = [w[0] for w in top_words]
        counts = [w[1] for w in top_words]
        
        # Reverse lists to have highest value at the top
        words.reverse()
        counts.reverse()
        
        ax.barh(words, counts, color='lightgreen')
        ax.set_xlabel('Count')
        ax.set_ylabel('Word')
        ax.set_title('Most Frequent Words')
        
        # Add count labels to the bars
        for i, v in enumerate(counts):
            ax.text(v + 0.1, i, str(v), va='center')
        
        # Embed the chart in the frame
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_sentiment_trend_chart(self, parent, tweets):
        # This chart will show hashtags grouped by sentiment
        frame = ttk.Frame(parent)
        parent.add(frame, text="Hashtags by Sentiment")
        
        # Group hashtags by sentiment
        positive_hashtags = []
        neutral_hashtags = []
        negative_hashtags = []
        
        for tweet in tweets:
            sentiment = tweet.get('sentiment', 'unknown')
            hashtags = tweet.get('hashtags', [])
            
            if sentiment == 'positive':
                positive_hashtags.extend(hashtags)
            elif sentiment == 'neutral':
                neutral_hashtags.extend(hashtags)
            elif sentiment == 'negative':
                negative_hashtags.extend(hashtags)
        
        # Count hashtags by sentiment
        positive_counts = Counter(positive_hashtags)
        neutral_counts = Counter(neutral_hashtags)
        negative_counts = Counter(negative_hashtags)
        
        # Get top hashtags from each sentiment
        top_positive = positive_counts.most_common(5)
        top_neutral = neutral_counts.most_common(5)
        top_negative = negative_counts.most_common(5)
        
        # Skip if no significant data
        if not (top_positive or top_neutral or top_negative):
            lbl = tk.Label(frame, text="No hashtag data available")
            lbl.pack(pady=50)
            return
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(6, 5), tight_layout=True)
        
        # Prepare data for grouped bar chart
        # Get all unique hashtags from top 5 of each sentiment
        all_hashtags = set()
        for h, _ in top_positive + top_neutral + top_negative:
            all_hashtags.add(h)
        
        # For better visualization, limit to top 10 overall
        if len(all_hashtags) > 10:
            # Count total occurrences of each hashtag
            total_counts = Counter()
            for h, c in top_positive + top_neutral + top_negative:
                total_counts[h] += c
            
            # Get top 10 hashtags
            all_hashtags = set([h for h, _ in total_counts.most_common(10)])
        
        all_hashtags = list(all_hashtags)  # Convert to list for indexing
        
        # Prepare data for each sentiment
        x = np.arange(len(all_hashtags))  # X-axis positions
        width = 0.25  # Width of bars
        
        # Get counts for each hashtag by sentiment
        pos_values = [positive_counts.get(h, 0) for h in all_hashtags]
        neu_values = [neutral_counts.get(h, 0) for h in all_hashtags]
        neg_values = [negative_counts.get(h, 0) for h in all_hashtags]
        
        # Create grouped bar chart
        ax.bar(x - width, pos_values, width, label='Positive', color='green')
        ax.bar(x, neu_values, width, label='Neutral', color='blue')
        ax.bar(x + width, neg_values, width, label='Negative', color='red')
        
        # Set chart labels and title
        ax.set_xlabel('Hashtags')
        ax.set_ylabel('Count')
        ax.set_title('Top Hashtags by Sentiment')
        ax.set_xticks(x)
        ax.set_xticklabels(all_hashtags, rotation=45, ha='right')
        ax.legend()
        
        # Add some spacing at the bottom for rotated labels
        plt.subplots_adjust(bottom=0.25)
        
        # Embed the chart in the frame
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = TweetAnalyzerApp(root)
    root.mainloop()