# Fact-Check & Q&A Social Media Bot

A Generative AI–powered bot that monitors social media posts, detects factual claims or questions, and automatically responds with concise, verified information — combining web search and LLM summarization to combat misinformation.

## 📋 Problem Statement

Develop a social media bot that monitors public posts and comments, identifies factual claims or questions, and responds with concise, verified information using web search and LLM-based summarization, fostering informed conversations and combating misinformation.

## 🧠 Approach & Architecture

The bot works as a 3-stage pipeline, repeated for every post:

1. **Claim Detection** (`detector.py`) — Uses an LLM (via Groq, running Llama 3.3) with few-shot prompting to classify whether a post contains a factual claim or question worth verifying, or is just casual conversation that should be ignored.
2. **Web Search / Retrieval** (`searcher.py`) — For posts flagged as claims, the bot queries the Tavily Search API to retrieve real, current web sources relevant to the claim.
3. **Summarization / Response Generation** (`responder.py`) — The retrieved search snippets are fed back into the LLM (Groq), which generates a short, natural-sounding reply stating whether the claim is true/false/partly true, grounded in the retrieved sources.
4. **Live Feed & Reply Posting** (`feed.py`) — Pulls real, live public posts from Mastodon (via hashtag timeline search), filtered to English-only. Generated replies are posted back live on Mastodon as genuine threaded replies to the original posts — the bot doesn't just analyze text, it actually responds publicly on a real platform.

This retrieve-then-generate pattern is known as **RAG (Retrieval-Augmented Generation)** — it ensures the bot's answers are based on real, current web data rather than the LLM's own (potentially outdated or hallucinated) knowledge.

`main.py` orchestrates all three stages and adds:
- **Deduplication** — tracks already-processed post IDs so the same post is never answered twice.
- **Polling loop** — re-checks the feed every 15 seconds, simulating real-time monitoring of a live social media stream.
- **Logging** — saves every decision and reply (with timestamps) to `bot_replies_log.json`.

### Why Mastodon instead of Reddit?

This bot was originally designed to monitor Reddit via its public API (using `PRAW`). However, Reddit introduced a new **"Responsible Builder Policy"** in 2026, which now requires explicit approval before any new API keys are issued — this approval process wasn't feasible to obtain within the project deadline.

Instead, the bot connects to **Mastodon** — a real, live, decentralized social media platform with a genuinely open API (instant API access, no approval process, free). The bot monitors Mastodon's `#news` hashtag timeline (the server used, mastodon.social, has its general public timeline disabled by admin policy, so hashtag search is used instead), filters to English-language posts, and **posts real fact-checked replies live** back onto the platform using the same account.

This is a true real-time, live-platform implementation — not a simulation. An earlier version of this project (see commit history) used a local JSON file to simulate a feed during initial development before Mastodon integration was completed; that approach is preserved in the commit history to show the project's development progression.

## 🛠️ Tech Stack

| Component | Tool | Purpose |
|---|---|---|
| LLM | [Groq](https://groq.com) (Llama 3.3 70B) | Claim detection + response summarization |
| Web Search | [Tavily](https://tavily.com) | Real-time fact retrieval |
| Feed | Local JSON file | Simulated social media posts (Reddit-style) |
| Language | Python 3.12 | Core implementation |

## 📂 Project Structure
```
factcheck-bot/
├── main.py                  # Orchestrates the full pipeline + polling loop
├── detector.py               # LLM-based claim/question classifier
├── searcher.py                # Tavily web search integration
├── responder.py               # LLM-based response generation (RAG)
├── sample_posts.json          # Simulated social media feed
├── test_read_feed.py           # Sanity check script for reading the feed
├── bot_replies_log.json        # Auto-generated log of all bot decisions/replies
├── requirements.txt            # Python dependencies
├── .gitignore
└── README.md
```
## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+ installed
- A free [Groq](https://console.groq.com) account and API key
- A free [Tavily](https://tavily.com) account and API key

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

4. Create a `.env` file in the project root with your API keys:
```
GROQ_API_KEY=your_groq_key_here
TAVILY_API_KEY=your_tavily_key_here
```
## ▶️ Usage

Run the bot:
```bash
python main.py
```

The bot will:
- Process all posts in `sample_posts.json`
- Skip posts with no factual claim
- Search the web and generate a fact-checked reply for posts that do contain a claim
- Save all results to `bot_replies_log.json`
- Keep polling every 15 seconds for new posts (press `Ctrl+C` to stop)

To test with new "incoming" posts, simply add a new entry to `sample_posts.json` while the bot is running — it will be picked up and processed automatically on the next polling cycle.

To test individual components separately:
```bash
python test_read_feed.py   # Verify the feed loads correctly
python detector.py          # Test claim detection only
python searcher.py           # Test web search only
python responder.py           # Test full search + response generation
```

## 🎥 Demo Video

[Link to unlisted YouTube demo video — add after recording]

## 🚧 Future Improvements

- Swap simulated feed for live Reddit API (PRAW) once API access is approved
- Add support for replying directly on the platform (auto-posting)
- Add a confidence score alongside TRUE/FALSE/PARTLY TRUE verdicts
- Rate-limit-aware backoff for production use
