"""
External tools and integrations for the research agent.
"""
import os


def search_web(queries: list[str]) -> list[dict]:
    """
    Call Tavily for each query and return a flat list of result dicts.
    Each dict has: query, title, url, content (snippet).

    Swap this out with any search API you prefer — DuckDuckGo, SerpAPI, etc.
    """
    from tavily import TavilyClient
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    results = []
    for q in queries:
        response = client.search(q, max_results=3)
        for r in response.get("results", []):
            results.append({
                "query": q,
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
            })
    return results
