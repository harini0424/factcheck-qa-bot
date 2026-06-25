import json
from detector import detect_claim
from searcher import search_claim
from responder import generate_response


def run_bot(feed_path="sample_posts.json"):
    with open(feed_path, "r") as f:
        posts = json.load(f)

    for post in posts:
        print(f"\n{'='*60}")
        print(f"Post by {post['author']}: {post['text']}")

        needs_check = detect_claim(post["text"])

        if not needs_check:
            print("→ No factual claim detected. Skipping.")
            continue

        print("→ Factual claim/question detected. Searching the web...")
        results = search_claim(post["text"])

        if not results:
            print("→ No search results found. Skipping.")
            continue

        print("→ Generating fact-checked reply...")
        reply = generate_response(post["text"], results)

        print(f"\n🤖 Bot reply: {reply}")


if __name__ == "__main__":
    run_bot()