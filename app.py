import json
from flask import Flask, render_template, redirect, url_for, request, session
from main import run_bot
from feed import get_post_by_id
from detector import detect_claim
from searcher import search_claim
from responder import generate_response, extract_verdict

app = Flask(__name__)
app.secret_key = "factcheck-bot-secret-key-change-if-needed"


def load_log():
    try:
        with open("bot_replies_log.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def compute_stats(log):
    stats = {"total": len(log), "true": 0, "false": 0, "partly": 0, "skipped": 0}
    for entry in log:
        if not entry.get("reply"):
            stats["skipped"] += 1
        elif entry.get("verdict") == "TRUE":
            stats["true"] += 1
        elif entry.get("verdict") == "FALSE":
            stats["false"] += 1
        elif entry.get("verdict") == "PARTLY TRUE":
            stats["partly"] += 1
    return stats


@app.route("/")
def home():
    log = list(reversed(load_log()))
    stats = compute_stats(log)
    check_result = session.pop("check_result", None)
    check_error = session.pop("check_error", None)
    return render_template("index.html", log=log, stats=stats, check_result=check_result, check_error=check_error)


@app.route("/run", methods=["POST"])
def run():
    hashtag = request.form.get("hashtag", "news").strip() or "news"
    run_bot(hashtag=hashtag)
    return redirect(url_for("home"))


@app.route("/check", methods=["POST"])
def check():
    raw_input = request.form.get("post_id", "").strip()
    post_id = raw_input.rstrip("/").split("/")[-1] if raw_input else ""

    if not post_id:
        session["check_error"] = "Please enter a post ID or URL."
        return redirect(url_for("home"))

    post = get_post_by_id(post_id)
    if post is None:
        session["check_error"] = "Post not found. Check the ID/URL and try again."
        return redirect(url_for("home"))

    needs_check = detect_claim(post["text"])
    result = {
        "author": post["author"],
        "text": post["text"],
        "needed_check": needs_check,
        "reply": None,
        "verdict": None,
        "sources": [],
    }

    if needs_check:
        results = search_claim(post["text"])
        if results:
            reply = generate_response(post["text"], results)
            result["reply"] = reply
            result["verdict"] = extract_verdict(reply)
            result["sources"] = [r["url"] for r in results][:3]

    session["check_result"] = result
    return redirect(url_for("home"))


@app.route("/delete", methods=["POST"])
def delete_entry():
    post_id = request.form.get("post_id", "")
    log = [entry for entry in load_log() if entry["post_id"] != post_id]
    with open("bot_replies_log.json", "w") as f:
        json.dump(log, f, indent=2)
    return redirect(url_for("home"))


@app.route("/clear", methods=["POST"])
def clear_all():
    with open("bot_replies_log.json", "w") as f:
        json.dump([], f)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)