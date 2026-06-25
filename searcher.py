import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

def search_claim(claim_text):
    """
    Searches the web for information related to the claim/question.
    Returns a list of result snippets with their source URLs.
    """
    response = client.search(
        query=claim_text,
        max_results=3,
    )

    results = []
    for r in response.get("results", []):
        results.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "content": r.get("content"),
        })
    return results


# Quick test when running this file directly
if __name__ == "__main__":
    test_claim = "Is the Great Wall of China visible from space with the naked eye?"
    results = search_claim(test_claim)
    for r in results:
        print(f"Title: {r['title']}")
        print(f"URL: {r['url']}")
        print(f"Snippet: {r['content'][:200]}...")
        print("---")