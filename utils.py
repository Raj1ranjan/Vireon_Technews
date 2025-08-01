def categorize_news(title, content):
    title_lower = title.lower()
    content_lower = content.lower()

    if any(keyword in title_lower or keyword in content_lower for keyword in ["ai", "artificial intelligence", "machine learning", "neural network"]):
        return "ai_news"
    elif any(keyword in title_lower or keyword in content_lower for keyword in ["game", "gaming", "xbox", "playstation", "nintendo", "steam"]):
        return "gaming_news"
    elif any(keyword in title_lower or keyword in content_lower for keyword in ["launch", "release", "unveil", "announce"]):
        return "new_launches"
    else:
        return "other_tech_news"
