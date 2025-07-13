# 🐦 Twitter Sentiment Analysis Tool

A powerful Python desktop application that scrapes tweets, analyzes sentiment using AI, and provides comprehensive visual analytics.

## ✨ Features

- **🔍 Tweet Scraping**: Automated tweet collection using Selenium WebDriver
- **🤖 AI Sentiment Analysis**: Powered by Groq API with Llama3-8b model
- **📊 MongoDB Storage**: Scalable data storage and retrieval
- **📈 Visual Analytics**: Interactive charts and sentiment distribution graphs
- **⚡ Real-time Processing**: Live sentiment analysis with GUI updates
- **🎯 Keyword Filtering**: Search-based tweet collection
- **📋 Comprehensive Analytics**: Hashtag trends, frequent words, and tweet classification


## 🚀 Installation

### Prerequisites

- Python 3.8+
- MongoDB installed and running
- Chrome browser
- Groq API key

### Setup Steps

1. **Clone the repository:**
```bash
git clone https://github.com/abdelilahbajjou/twitter-sentiment-analysis.git
cd twitter-sentiment-analysis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up API key:**
   - Get your Groq API key from [https://console.groq.com/](https://console.groq.com/)
   - Replace the API key in `llama_sentiment.py` or set as environment variable:
   ```bash
   export GROQ_API_KEY="your_api_key_here"
   ```

4. **Download ChromeDriver:**
   - Download from [https://chromedriver.chromium.org/](https://chromedriver.chromium.org/)
   - Place `chromedriver.exe` in the project directory
   - Or use webdriver-manager (included in requirements) for automatic management

5. **Start MongoDB:**
   - Ensure MongoDB is running on `localhost:27017`

6. ** Open a Session:**
   -Install the EditThisCookie extension from the Chrome Web Store
   -Login to your Twitter/X account, then click the extension icon and export cookies as twitter_cookies.json
   -Never share this file - it contains your authentication data and gives full account access
   -Consider using Twitter's official API v2 for production applications instead of cookie-based scraping
## 🎯 Usage

### Running the Application

```bash
python app.py
```

### Using the Interface

1. **Enter Search Keyword**: Type your search term (e.g., "climate change", "iPhone", "bitcoin")
2. **Start Scraping**: Click "Start Scraping" to begin data collection
3. **View Results**: Switch between tabs to explore different views:
   - **Tweets Tab**: All scraped tweets with sentiment labels
   - **Analytics Tab**: Hashtag trends, frequent words, best/worst tweets
   - **Graphs Tab**: Visual charts showing sentiment distribution and trends
4. **Clear Database**: Use "Clear DB" to reset stored data

### Key Features

- **Real-time Processing**: Watch sentiment analysis happen in real-time
- **Smart Deduplication**: Prevents duplicate tweets using MongoDB upsert
- **Comprehensive Analytics**: Detailed insights into tweet patterns
- **Visual Graphs**: Multiple chart types for data visualization
- **Export Friendly**: Data stored in MongoDB for easy export

## 🏗️ Technical Architecture

### Technology Stack

- **Frontend**: Tkinter GUI with matplotlib integration
- **Backend**: MongoDB for data persistence
- **AI Processing**: Groq API with Llama3-8b model
- **Web Scraping**: Selenium with Chrome WebDriver
- **Data Visualization**: Matplotlib with Tkinter integration

### File Structure

```
twitter-sentiment-analysis/
├── app.py                    # Main GUI application
├── twitter_scraper.py        # Web scraping functionality
├── llama_sentiment.py        # AI sentiment analysis
├── mongodb_handler.py        # Database operations
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
└── chromedriver.exe         # Chrome driver (download separately)
```

## ⚙️ Configuration

### API Configuration

Update the Groq API key in `llama_sentiment.py`:
```python
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_api_key_here")
```

### Database Configuration

MongoDB connection settings in `mongodb_handler.py`:
```python
client = MongoClient("mongodb://localhost:27017/")
db = client["twitter_db"]
```

### Scraping Configuration

Adjust scraping parameters in `twitter_scraper.py`:
```python
def scrape_tweets(keyword, max_tweets=20, headless=True):
    # Modify max_tweets, headless mode, etc.
```

## 📊 Data Model

### Tweet Document Structure

```python
{
    "username": "string",
    "text": "string",          # Original tweet text
    "hashtags": ["#example"], # Extracted hashtags
    "clean_text": "string",   # Cleaned text for analysis
    "sentiment": "positive",  # AI classification
    "timestamp": "datetime",  # Processing timestamp
    "keyword": "string"       # Search keyword used
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include error handling
- Test thoroughly before submitting

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Important Notes

### Security
- Never commit API keys or sensitive data
- Use environment variables for configuration
- Twitter cookies are excluded from version control

### Legal Compliance
- This tool is for educational and research purposes
- Ensure compliance with Twitter's Terms of Service
- Respect rate limits and usage policies

### Performance
- MongoDB provides scalable storage
- Selenium may be slow for large datasets
- Consider implementing request delays to avoid blocking

## 🐛 Troubleshooting

### Common Issues

1. **ChromeDriver not found**: Download ChromeDriver and place in project directory
2. **MongoDB connection failed**: Ensure MongoDB is running on localhost:27017
3. **API key errors**: Check Groq API key configuration
4. **Selenium errors**: Update Chrome browser and ChromeDriver to latest versions

### Getting Help

- Check the Issues tab for common problems
- Create a new issue with detailed error descriptions
- Include your Python version and OS information

## 🔮 Future Enhancements

- [ ] Real-time streaming support
- [ ] Multiple social media platforms
- [ ] Advanced sentiment metrics
- [ ] Export to CSV/Excel
- [ ] Custom AI model training
- [ ] Web-based interface
- [ ] Docker containerization

## 👏 Acknowledgments

- Groq for providing the AI API
- MongoDB for database technology
- Selenium WebDriver community
- Python data science ecosystem

---

**Star ⭐ this repository if you find it helpful!**