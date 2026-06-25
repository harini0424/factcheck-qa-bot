import os
from dotenv import load_dotenv
from groq import Groq

# Load API keys from .env file
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def detect_claim(post_text):
    """
    Asks the LLM whether this post contains a factual claim or question
    worth fact-checking. Returns True or False.
    """
    prompt = f"""You are a classifier for a fact-checking bot. Decide if a social media post 
contains ANY factual claim or question that could be checked against real-world information — 
even if phrased casually, as "did you know", or as something that sounds well-known.

Examples:
Post: "Did you know the Eiffel Tower was originally meant for Barcelona?"
Answer: YES

Post: "I love pizza so much, ordering some right now lol"
Answer: NO

Post: "Is it true that goldfish have a 3-second memory?"
Answer: YES

Post: "Ugh, Mondays are the worst"
Answer: NO

Now classify this post. Reply with ONLY one word: YES or NO.

Post: "{post_text}"
Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    answer = response.choices[0].message.content.strip().upper()
    return "YES" in answer


# Quick test when running this file directly
if __name__ == "__main__":
    test_posts = [
        "Did you know the Great Wall of China is visible from space with the naked eye?",
        "I love pizza so much, ordering some right now lol",
    ]
    for p in test_posts:
        result = detect_claim(p)
        print(f"Post: {p}\n  → Needs fact-check? {result}\n")