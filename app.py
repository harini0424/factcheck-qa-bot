import json
import csv
import io
from collections import defaultdict
from flask import Flask, render_template, redirect, url_for, request, session, Response
from main import run_bot
from feed import get_post_by_id
from detector import detect_claim
from searcher import search_claim
from responder import generate_response, extract_verdict, assess_severity

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

    checked = stats["true"] + stats["false"] + stats["partly"]
    stats["checked"] = checked
    stats["false_pct"] = round((stats["false"] / checked) * 100) if checked > 0 else 0
    return stats

def compute_trend(log):
    """Groups entries by date (YYYY-MM-DD) and counts verdicts per day."""
    by_date = defaultdict(lambda: {"true": 0, "false": 0, "partly": 0})
    for entry in log:
        if not entry.get("reply"):
            continue
        date = entry.get("timestamp", "")[:10]
        if not date:
            continue
        verdict = entry.get("verdict")
        if verdict == "TRUE":
            by_date[date]["true"] += 1
        elif verdict == "FALSE":
            by_date[date]["false"] += 1
        elif verdict == "PARTLY TRUE":
            by_date[date]["partly"] += 1

    dates = sorted(by_date.keys())
    return {
        "dates": dates,
        "true": [by_date[d]["true"] for d in dates],
        "false": [by_date[d]["false"] for d in dates],
        "partly": [by_date[d]["partly"] for d in dates],
    }


@app.route("/")
def home():
    log = list(reversed(load_log()))
    stats = compute_stats(log)
    trend = compute_trend(load_log())
    check_result = session.pop("check_result", None)
    check_error = session.pop("check_error", None)
    return render_template("index.html", log=log, stats=stats, trend=trend, check_result=check_result, check_error=check_error)


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
        "severity": None,
        "sources": [],
    }

    if needs_check:
        results = search_claim(post["text"])
        if results:
            reply = generate_response(post["text"], results)
            verdict = extract_verdict(reply)
            result["reply"] = reply
            result["verdict"] = verdict
            result["severity"] = assess_severity(post["text"], verdict)
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


@app.route("/export")
def export_csv():
    log = load_log()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "author", "text", "verdict", "severity", "reply", "sources"])
    for entry in log:
        writer.writerow([
            entry.get("timestamp", ""),
            entry.get("author", ""),
            entry.get("text", ""),
            entry.get("verdict", ""),
            entry.get("severity", ""),
            entry.get("reply", ""),
            "; ".join(entry.get("sources", [])),
        ])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=factcheck_report.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True)