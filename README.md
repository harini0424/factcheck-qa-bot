# Fact-Check & Q&A Social Media Bot

This is a bot that watches live posts on social media, figures out which ones are making a factual claim (vs. just casual chat), checks those claims against real web sources, and replies with a short, honest verdict — TRUE, FALSE, or PARTLY TRUE. It also has a small web dashboard so you can run it, watch what it's doing, and manually check any post you want.

Built for the assignment: develop a bot that monitors posts, identifies claims/questions, and responds with verified info using web search + LLM summarization, to help fight misinformation.

## How it actually works

There are four pieces, and each one does one job:

**1. Getting posts — `feed.py`**
Pulls real, live posts off Mastodon, searched by hashtag (currently `#news` by default). I filter out non-English posts using Mastodon's language tag (not perfect — some posts mislabel their language, so a few non-English ones slip through sometimes).

**2. Deciding if a post is worth checking — `detector.py`**
Most posts on social media are just people talking, not making claims. This step asks an LLM (Groq, running Llama 3.3) a simple question: does this post contain something checkable? I had to fix this with a few examples in the prompt early on — without them, the model was way too conservative and said "no" to almost everything, even obvious claims like "the Great Wall is visible from space."

**3. Actually checking it — `searcher.py`**
For anything flagged as a claim, this calls the Tavily search API and pulls back a few real web results.

**4. Writing the reply — `responder.py`**
Feeds those search results back into the LLM and asks it to write a short, natural reply with a verdict. This is the "RAG" part (retrieval-augmented generation) — the LLM isn't guessing from memory, it's basing the answer on what was actually just found on the web.

`main.py` ties all of this together, keeps track of which posts it's already replied to (so it doesn't double-reply), and can actually post the generated reply back on Mastodon for real.

## The dashboard

I added a small Flask website on top of the bot (`app.py` + `templates/index.html`) because running everything from the terminal only felt limited. From the dashboard you can:
- Click a button to run the bot on demand, on whatever hashtag you type in
- Paste any Mastodon post link and check that one specific post immediately
- See a TRUE/FALSE/PARTLY TRUE badge and the actual source links for every reply
- See quick stats — how many posts were true, false, etc.
- Delete or clear entries
- It also auto-refreshes every 20 seconds so it feels live without you doing anything

## Why Mastodon and not Reddit

I originally built this to run on Reddit. I got the whole pipeline working with a simulated/sample feed first, then went to actually connect to Reddit's API — and that's when I found out Reddit rolled out a new policy in 2026 (they call it the "Responsible Builder Policy") that requires getting approved before you can even get API keys. That wasn't something I could realistically get done before the deadline.

So I switched to Mastodon instead. It's a real social platform, and unlike Reddit/Twitter, you get full API access instantly for free — no approval queue. One annoying thing I ran into: the server I'm using (mastodon.social) has its general public timeline turned off by the admins, so I had to switch to pulling posts by hashtag instead, which works fine.

If you look at the commit history, you can see the project actually started with a local JSON file standing in for a feed, before I got the live Mastodon connection working — I kept that history rather than rewriting it, since it shows how the project actually progressed.

## Tech stack

| Piece | Tool | What it's for |
|---|---|---|
| LLM | Groq (Llama 3.3 70B) | deciding what's a claim + writing the reply |
| Search | Tavily | pulling real web evidence |
| Platform | Mastodon | where the posts come from + where replies get posted |
| Web framework | Flask | the dashboard |
| Language | Python 3.12 | everything |

## Project structure
## Setup

You'll need Python 3.10+, and free accounts/API keys for Groq, Tavily, and Mastodon.

```bash
git clone https://github.com/harini0424/factcheck-qa-bot.git
cd factcheck-qa-bot

python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows
source venv/bin/activate         # Mac/Linux

pip install -r requirements.txt
```

Then create a `.env` file in the project folder with:
## Running it

**Dashboard (the easier way):**
```bash
python app.py
```
Then open http://127.0.0.1:5000 in your browser.

**Or run it straight from the terminal**, which loops forever checking for new posts every 15 seconds:
```bash
python main.py
```

**About posting real replies:** by default `DRY_RUN = True` in `main.py`, so it won't actually post anything — it just shows what it would say. Change it to `False` if you want it to post for real on Mastodon.

You can also test each piece on its own:
```bash
python feed.py
python detector.py
python searcher.py
python responder.py
```

## Demo video

[link goes here once recorded]

## Things I'd improve with more time

- Better language filtering — Mastodon's language tags aren't always accurate
- Support other platforms through the same feed structure (Bluesky would be an easy next one)
- Some kind of rate-limit handling if this ran continuously for a long time
