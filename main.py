import json
import time
from datetime import datetime
from detector import detect_claim
from searcher import search_claim
from responder import generate_response, extract_verdict
from feed import get_recent_posts, post_reply

DRY_RUN = True  # Set to False when you're ready to actually post replies live


def get_already_processed_ids(log_path="bot_replies_log.json"):
    """Reads the log file (if it exists) to find which post IDs we've already handled."""
    try:
        with open(log_path, "r") as f:
            log = json.load(f)
        return {entry["post_id"] for entry in log}
    except FileNotFoundError:
        return set()


def run_bot(log_path="bot_replies_log.json", hashtag="news"):
    posts = get_recent_posts(limit=5, hashtag=hashtag)

    processed_ids = get_already_processed_ids(log_path)
    log = []
    new_posts_found = False

    for post in posts:
        if post["id"] in processed_ids:
            continue  # already handled in a previous run, skip it

        new_posts_found = True
        print(f"\n{'='*60}")
        print(f"New post by {post['author']}: {post['text']}")

        needs_check = detect_claim(post["text"])

        entry = {
            "post_id": post["id"],
            "author": post["author"],
            "text": post["text"],
            "needed_check": needs_check,
            "reply": None,
            "verdict": None,
            "sources": [],
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
        verdict = extract_verdict(reply)

        entry["reply"] = reply
        entry["verdict"] = verdict
        entry["sources"] = [r["url"] for r in results][:3]

        print(f"\n🤖 Bot reply ({verdict}): {reply}")

        if DRY_RUN:
            print("   (DRY_RUN is True — not actually posting to Mastodon)")
        else:
            post_reply(reply, post["id"])
            print("   ✅ Reply posted live on Mastodon!")

        log.append(entry)

    if not new_posts_found:
        print("No new posts to process. (Bot is up to date.)")
        return

    existing_log = []
    try:
        with open(log_path, "r") as f:
            existing_log = json.load(f)
    except FileNotFoundError:
        pass

    full_log = existing_log + log
    with open(log_path, "w") as f:
        json.dump(full_log, f, indent=2)
    print(f"\n✅ Saved {len(log)} new entries to {log_path}")


if __name__ == "__main__":
    print("🔍 Bot monitoring started. Checking feed every 15 seconds... (Ctrl+C to stop)\n")
    while True:
        run_bot()
        time.sleep(15)