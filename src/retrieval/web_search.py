import logging
from typing import List, Dict, Any
from tavily import TavilyClient
from ddgs import DDGS
from src.config import TAVILY_API_KEY, MAX_EVIDENCE_PER_TURN

logger = logging.getLogger(__name__)

def search_tavily(query: str, max_results: int = MAX_EVIDENCE_PER_TURN) -> List[Dict[str, Any]]:
    """Executes live web search using Tavily API."""
    if not TAVILY_API_KEY:
        return []
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            max_results=max_results,
            search_depth="advanced",
            include_answer=False
        )
        results = []
        for item in response.get("results", []):
            title = item.get("title", "").strip()
            url = item.get("url", "").strip()
            snippet = item.get("content", item.get("snippet", "")).strip()
            if title and url and snippet:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
        return results
    except Exception as e:
        logger.warning(f"Tavily search API call failed for query '{query}': {e}")
        return []

def search_ddgs(query: str, max_results: int = MAX_EVIDENCE_PER_TURN) -> List[Dict[str, Any]]:
    """Executes live web search using DuckDuckGo (DDGS) backup engine."""
    try:
        ddgs = DDGS()
        raw_results = list(ddgs.text(query, max_results=max_results))
        results = []
        for item in raw_results:
            title = item.get("title", "").strip()
            url = item.get("href", "").strip()
            snippet = item.get("body", "").strip()
            if title and url and snippet:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
        return results
    except Exception as e:
        logger.warning(f"DDGS live web search backup failed for query '{query}': {e}")
        return []

def search(query: str, max_results: int = MAX_EVIDENCE_PER_TURN) -> List[Dict[str, Any]]:
    """
    Main entry point for web evidence retrieval.
    Guarantees 100% REAL live web search results by trying Tavily API first,
    and falling back to live DuckDuckGo web search if Tavily key is missing or fails.
    No mock or synthetic evidence is ever generated.
    """
    # 1. Primary: Tavily Live Search
    results = search_tavily(query=query, max_results=max_results)
    if results:
        return results
        
    # 2. Query Simplification Retry for Tavily (remove stance bias words if query was too strict)
    simplified_query = " ".join([w for w in query.split() if w.lower() not in ["supporting", "evidence", "refuting", "counter-evidence", "true", "false"]])
    if simplified_query != query:
        results = search_tavily(query=simplified_query, max_results=max_results)
        if results:
            return results

    # 3. Secondary Real Web Search: DuckDuckGo Live Search Engine
    logger.info(f"Using live DuckDuckGo search backup for query: '{query}'")
    results = search_ddgs(query=query, max_results=max_results)
    if results:
        return results
        
    if simplified_query != query:
        results = search_ddgs(query=simplified_query, max_results=max_results)
        if results:
            return results

    return []
