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
    Filters to English-only posts.
    Returns a list of posts in the format our bot expects:
    {id, author, text}
    """
    timeline = mastodon.timeline_hashtag(hashtag, limit=limit * 4)  # fetch extra, since we'll filter some out

    posts = []
    for status in timeline:
        if status.get("language") != "en":
            continue  # skip non-English posts

        clean_text = re.sub(r"<[^>]+>", "", status["content"])      # strip HTML tags
        clean_text = re.sub(r"https?://\S+", "", clean_text)         # strip URLs
        clean_text = re.sub(r"#\w+", "", clean_text)                  # strip hashtags
        clean_text = clean_text.strip()

        if not clean_text:
            continue  # skip if nothing meaningful left after cleanup

        posts.append({
            "id": str(status["id"]),
            "author": status["account"]["username"],
            "text": clean_text,
        })

        if len(posts) >= limit:
            break

    return posts
def get_post_by_id(post_id):
    """
    Fetches a single specific post by its Mastodon ID.
    Returns it in the same {id, author, text} format, or None if not found.
    """
    try:
        status = mastodon.status(post_id)
    except Exception:
        return None

    clean_text = re.sub(r"<[^>]+>", "", status["content"])
    clean_text = re.sub(r"https?://\S+", "", clean_text)
    clean_text = re.sub(r"#\w+", "", clean_text)
    clean_text = clean_text.strip()

    return {
        "id": str(status["id"]),
        "author": status["account"]["username"],
        "text": clean_text,
    }


def post_reply(reply_text, in_reply_to_id):
    """
    Posts an actual reply on Mastodon, attached to the original post.
    """
    mastodon.status_post(
        status=reply_text,
        in_reply_to_id=in_reply_to_id,
        visibility="public",
    )


# Quick test when running this file directly
if __name__ == "__main__":
    posts = get_recent_posts(limit=5)
    for p in posts:
        print(f"[{p['id']}] {p['author']}: {p['text']}")