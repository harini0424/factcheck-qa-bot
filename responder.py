import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate_response(claim_text, search_results):
    """
    Takes the original claim/question and search result snippets,
    and asks the LLM to write a short, clear, fact-based reply.
    """
    sources_text = ""
    for i, r in enumerate(search_results, 1):
        sources_text += f"Source {i} ({r['url']}): {r['content'][:300]}\n\n"

    prompt = f"""You are a helpful fact-checking bot replying to a social media post.

Original post: "{claim_text}"

Here is what web search found:
{sources_text}

Write a short, friendly, factual reply (2-3 sentences max) that:
- Clearly states whether the claim is TRUE, FALSE, or PARTLY TRUE
- Briefly explains why, based on the sources
- Does NOT sound robotic or overly formal
- Does NOT include raw URLs in the reply text itself

Reply:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def extract_verdict(reply_text):
    """
    Scans the generated reply for a TRUE / FALSE / PARTLY TRUE verdict,
    so the UI can show a colored badge instead of just plain text.
    """
    text = reply_text.upper()
    if "PARTLY TRUE" in text or "PARTIALLY TRUE" in text:
        return "PARTLY TRUE"
    elif "FALSE" in text:
        return "FALSE"
    elif "TRUE" in text:
        return "TRUE"
    else:
        return "UNKNOWN"


# Quick test when running this file directly
if __name__ == "__main__":
    from searcher import search_claim

    claim = "Is the Great Wall of China visible from space with the naked eye?"
    results = search_claim(claim)
    reply = generate_response(claim, results)
    verdict = extract_verdict(reply)
    print("Generated reply:\n")
    print(reply)
    print(f"\nVerdict: {verdict}")