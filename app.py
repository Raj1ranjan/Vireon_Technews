import os
from flask import Flask, render_template_string, url_for, abort
from news_fetcher import fetch_all_news
import requests
from collections import defaultdict
import time
from dotenv import load_dotenv
load_dotenv()

import hashlib
# --- NEW: Import the summarize_article function from summarizer.py ---
from summarizer import summarize_article, API_KEY, MODEL_NAME 

# No need to load API_KEY directly here anymore, it's handled in summarizer.py
# API_KEY = os.getenv("OPENROUTER_API_KEY")
# if not API_KEY:
#     print("WARNING: OPENROUTER_API_KEY environment variable not set. Summarization will fail.")

app = Flask(__name__)

# --- Caching Mechanism ---
# Store articles in a dictionary keyed by a unique ID
cached_articles_by_id = {}
last_fetch_time = 0
CACHE_DURATION_SECONDS = 3600  # Cache for 1 hour

def generate_article_id(article):
    """Generates a unique ID for an article based on its title and URL."""
    unique_string = f"{article.get('title', '')}-{article.get('url', '')}"
    return hashlib.sha256(unique_string.encode()).hexdigest()[:10]


def refresh_news_cache():
    global last_fetch_time
    global cached_articles_by_id

    if (time.time() - last_fetch_time) > CACHE_DURATION_SECONDS or not cached_articles_by_id:
        print("Refreshing news cache...")
        raw_articles = fetch_all_news()
        temp_articles_by_id = {}

        for article in raw_articles:
            article_id = generate_article_id(article)
            article_data = {
                "id": article_id,
                "title": article.get("title", "No title"),
                "url": article.get("url", "#"),
                "content": article.get("content") or article.get("description") or "",
                "source": article.get("source", {}).get("name", "Unknown Source"),
                "category": article.get("category", "General").replace(" ", "_").lower()
            }
            temp_articles_by_id[article_id] = article_data

        cached_articles_by_id = temp_articles_by_id
        last_fetch_time = time.time()
    else:
        print("Using cached news data.")

# --- REMOVED: The old summarize_article function from app.py ---
# This function is now in summarizer.py and imported.
# def summarize_article(text, word_limit=None):
#     summary_key = f"{hash(text)}_{word_limit}"
#     if summary_key in app.config.get('SUMMARY_CACHE', {}):
#         return app.config['SUMMARY_CACHE'][summary_key]
#     # ... rest of the old summarization logic ...


# Home route - shows list of all news article titles
@app.route("/")
def home():
    refresh_news_cache()

    articles = list(cached_articles_by_id.values())
    articles.sort(key=lambda x: x['title'])

    if not articles:
        return render_template_string("""
        <html>
        <head>
            <title>Tech News</title>
            <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        </head>
        <body>
            <h1>📰 Latest Tech News</h1>
            <p>No tech news found at the moment. Please try again later!</p>
        </body>
        </html>
        """)

    html = """
    <html>
    <head>
        <title>Latest Tech News</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <h1>📰 Latest Tech News</h1>
        <div class="news-list">
            {% for article in articles %}
                <div class="news-item">
                    <a href="{{ url_for('article_detail', article_id=article.id) }}">{{ article.title }}</a>
                </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """
    return render_template_string(html, articles=articles)

# New route for individual article details and summary
@app.route("/article/<string:article_id>")
def article_detail(article_id):
    refresh_news_cache()

    article = cached_articles_by_id.get(article_id)

    if not article:
        abort(404)

    # --- UPDATED: Call the imported summarize_article function ---
    # Note: Your new summarizer.py doesn't take a word_limit argument directly in the function call,
    # it's handled by the system prompt within summarizer.py.
    summary = summarize_article(article["content"])

    html = """
    <html>
    <head>
        <title>{{ article.title }} - Summarized News</title>
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    </head>
    <body>
        <h1>📄 {{ article.title }}</h1>
        <p class="nav-link"><a href="{{ url_for('home') }}">Back to All News</a></p>
        <div class="card">
            <div class="summary">{{ summary }}</div>
            <div class="source">Source: {{ article.source }}</div>
            <div class="original-link"><a href="{{ article.url }}" target="_blank">Read Original Article</a></div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, article=article, summary=summary)

if __name__ == "__main__":
    refresh_news_cache()
    app.run(debug=True)