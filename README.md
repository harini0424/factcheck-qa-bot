# Fact-Check & Q&A Social Media Bot

A Generative AI–powered bot that monitors live social media posts, detects factual claims or questions, verifies them using web search, and responds with concise, fact-checked information — combining LLM reasoning with retrieval-augmented generation (RAG) to combat misinformation in real time.

Includes a Flask web dashboard for live monitoring, manual post verification, and activity management.

## 📋 Problem Statement

Develop a social media bot that monitors public posts and comments, identifies factual claims or questions, and responds with concise, verified information using web search and LLM-based summarization, fostering informed conversations and combating misinformation.

## 🧠 Approach & Architecture

The bot runs a 4-stage pipeline for every post:

1. **Live Feed** (`feed.py`) — Pulls real, live public posts from **Mastodon** (via hashtag timeline search, e.g. `#news`), filtered to English-language posts. Also supports fetching a single specific post by ID/URL for manual verification.
2. **Claim Detection** (`detector.py`) — Uses an LLM (via Groq, running Llama 3.3) with few-shot prompting to classify whether a post contains a factual claim or question worth verifying, or is just casual conversation to ignore.
3. **Web Search / Retrieval** (`searcher.py`) — For flagged posts, queries the **Tavily Search API** to retrieve real, current web sources relevant to the claim.
4. **Summarization / Response Generation** (`responder.py`) — Retrieved search snippets are fed back into the LLM (Groq), which generates a short, natural reply stating whether the claim is TRUE, FALSE, or PARTLY TRUE, grounded in the retrieved sources. A verdict is also extracted for UI display.

This retrieve-then-generate pattern is **RAG (Retrieval-Augmented Generation)** — it ensures the bot's answers are based on real, current web data rather than the LLM's own (potentially outdated or hallucinated) knowledge.

`main.py` orchestrates the full pipeline and adds:
- **Deduplication** — tracks already-processed post IDs so the same post is never answered twice.
- **Live reply posting** — generated replies are posted back live on Mastodon as genuine threaded replies (toggle via `DRY_RUN`).
- **Logging** — saves every decision/reply (with verdict, sources, and timestamp) to `bot_replies_log.json`.

### Web Dashboard (`app.py` + `templates/index.html`)

A Flask-based dashboard provides:
- **Run Bot Now** — triggers a live pipeline pass on a chosen hashtag
- **Check a Specific Post** — paste any Mastodon post URL or ID to verify it on demand, without waiting for the next polling cycle
- **Verdict badges** — color-coded TRUE / FALSE / PARTLY TRUE indicators
- **Source links** — clickable references to the web sources used for each verdict
- **Stats summary** — live counts of total/true/false/partly-true/skipped posts
- **Auto-refresh** — dashboard reloads periodically to reflect new activity
- **Re-check / Delete / Clear All** — manage individual entries or the whole log

### Why Mastodon instead of Reddit?

This bot was originally designed to monitor Reddit via its public API (using `PRAW`). However, Reddit introduced a new **"Responsible Builder Policy"** in 2026, which now requires explicit approval before any new API keys are issued — not feasible within the project deadline.

Instead, the bot connects to **Mastodon** — a real, live, decentralized social platform with a genuinely open API (instant access, no approval process, free). Mastodon.social's general public timeline is disabled by server policy, so the bot uses hashtag-based timeline search instead. This is a true real-time, live-platform implementation — not a simulation. (An earlier development version used a local JSON file to simulate a feed; see commit history for the project's full progression.)

## 🛠️ Tech Stack

| Component | Tool | Purpose |
|---|---|---|
| LLM | [Groq](https://groq.com) (Llama 3.3 70B) | Claim detection + response summarization |
| Web Search | [Tavily](https://tavily.com) | Real-time fact retrieval |
| Social Platform | [Mastodon](https://mastodon.social) | Live post feed + reply posting |
| Web Framework | Flask | Dashboard UI |
| Language | Python 3.12 | Core implementation |

## 📂 Project Structure
## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- A free [Groq](https://console.groq.com) account and API key
- A free [Tavily](https://tavily.com) account and API key
- A free [Mastodon](https://mastodon.social) account and an application access token (read + write scopes)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/harini0424/factcheck-qa-bot.git
cd factcheck-qa-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:
## ▶️ Usage

### Run the web dashboard (recommended)
```bash
python app.py
```
Then open **http://127.0.0.1:5000** in your browser. Use "Run Bot Now" to process live posts, or "Check a Specific Post" to verify any single post by URL/ID.

### Run the bot standalone in the terminal (continuous polling)
```bash
python main.py
```
Checks the feed every 15 seconds and prints/logs results until stopped (`Ctrl+C`).

### ⚠️ Going live (posting real replies)
By default, `DRY_RUN = True` in `main.py` — the bot will **not** post anything publicly; it only logs what it would post. Set `DRY_RUN = False` to enable real reply-posting to Mastodon.

### Test individual components
```bash
python feed.py        # Test live Mastodon feed fetching
python detector.py     # Test claim detection
python searcher.py     # Test web search
python responder.py    # Test full search + response generation
```

## 🎥 Demo Video

[Link to unlisted YouTube demo video — add after recording]

## 🚧 Future Improvements

- Auto-detect post language more reliably (Mastodon's self-reported language tag is occasionally inaccurate)
- Support additional platforms (e.g. Bluesky) via the same modular feed interface
- Add authentication for multi-user dashboard access if deployed publicly
- Rate-limit-aware backoff for sustained production use