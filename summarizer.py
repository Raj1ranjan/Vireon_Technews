import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get API key and model from environment
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")

def summarize_article(text):
    if not text or len(text.strip()) < 20:
        return "Not enough content to summarize."

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",     # Required by OpenRouter
        "X-Title": "Tech News Summarizer App"   # Optional
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes tech news in 50–100 words."},
            {"role": "user", "content": text}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)

        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except requests.exceptions.HTTPError as http_err:
        print(f"[HTTP ERROR] {http_err}")
        return "Failed to summarize article (HTTP error)."
    except Exception as e:
        print(f"[ERROR] {e}")
        return "Failed to summarize article."

# Debug test
if __name__ == "__main__":
    sample = "Apple just launched a new iPhone with AI-powered photography features and a more power-efficient chip. This marks a major shift toward on-device intelligence."
    print(summarize_article(sample))
