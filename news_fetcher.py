import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Load GNews API Key from environment
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

def fetch_all_news():
    if not GNEWS_API_KEY:
        print("⚠️ GNEWS_API_KEY is not set. Please check your .env file.")
        return []

    url = f"https://gnews.io/api/v4/top-headlines?topic=technology&lang=en&max=20&token={GNEWS_API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises error for HTTP codes like 401, 500 etc.
        data = response.json()

        articles = []
        for item in data.get("articles", []):
            articles.append({
                "title": item.get("title", "No title"),
                "url": item.get("url", "#"),
                "description": item.get("description", ""),
                "content": item.get("content", "") or item.get("description", ""),
                "source": {"name": item.get("source", {}).get("name", "Unknown Source")},
                "category": "technology",  # GNews doesn't include categories directly
                "image": item.get("image")  # Optional: store image URL for future use
            })

        return articles

    except requests.exceptions.RequestException as e:
        print("🔴 Error while fetching news:", e)
        return []
