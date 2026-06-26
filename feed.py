import os
import re
from dotenv import load_dotenv
from mastodon import Mastodon

load_dotenv()

mastodon = Mastodon(
    access_token=os.environ.get("MASTODON_ACCESS_TOKEN"),
    api_base_url=os.environ.get("MASTODON_API_BASE_URL"),
)


def get_recent_posts(limit=5, hashtag="news"):
    """
    Fetches recent public posts from Mastodon (via hashtag timeline,
    since this server's general public timeline is disabled).
    Returns a list of posts in the format our bot expects:
    {id, author, text}
    """
    timeline = mastodon.timeline_hashtag(hashtag, limit=limit)

    posts = []
    for status in timeline:
        clean_text = re.sub(r"<[^>]+>", "", status["content"])  # strip HTML tags
        clean_text = re.sub(r"https?://\S+", "", clean_text)     # strip URLs
        clean_text = re.sub(r"#\w+", "", clean_text)              # strip hashtags
        clean_text = clean_text.strip()
        posts.append({
            "id": str(status["id"]),
            "author": status["account"]["username"],
            "text": clean_text,
        })
    return posts


# Quick test when running this file directly
if __name__ == "__main__":
    posts = get_recent_posts(limit=5)
    for p in posts:
        print(f"[{p['id']}] {p['author']}: {p['text']}")