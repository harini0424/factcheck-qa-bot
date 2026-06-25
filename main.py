import json
from datetime import datetime
from detector import detect_claim
from searcher import search_claim
from responder import generate_response


def run_bot(feed_path="sample_posts.json", log_path="bot_replies_log.json"):
    with open(feed_path, "r") as f:
        posts = json.load(f)

    log = []

    for post in posts:
        print(f"\n{'='*60}")
        print(f"Post by {post['author']}: {post['text']}")

        needs_check = detect_claim(post["text"])

        entry = {
            "post_id": post["id"],
            "author": post["author"],
            "text": post["text"],
            "needed_check": needs_check,
            "reply": None,
            "timestamp": datetime.now().isoformat(),
        }

        if not needs_check:
            print("→ No factual claim detected. Skipping.")
            log.append(entry)
            continue

        print("→ Factual claim/question detected. Searching the web...")
        results = search_claim(post["text"])

        if not results:
            print("→ No search results found. Skipping.")
            log.append(entry)
            continue

        print("→ Generating fact-checked reply...")
        reply = generate_response(post["text"], results)
        entry["reply"] = reply

        print(f"\n🤖 Bot reply: {reply}")
        log.append(entry)

    # Save everything to a log file
    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)
    print(f"\n✅ Saved {len(log)} entries to {log_path}")


if __name__ == "__main__":
    run_bot()