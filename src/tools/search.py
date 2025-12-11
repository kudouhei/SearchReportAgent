""" Search tool
Support multiple search engines, using Tavily Search API
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from tavily import TavilyClient

@dataclass
class SearchResult:
    """
    Search result
    """
    title: str
    url: str
    content: str
    score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the SearchResult to a dictionary
        """
        return {
            'title': self.title,
            'url': self.url,
            'content': self.content,
            'score': self.score,
        }

class TavilySearch:
    """
    Tavily Search Tool
    """
    def __init__(self, api_key: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("TAVILY_API_KEY")
            if not api_key:
                raise ValueError("Tavily API key is not set")

        self.api_key = api_key
        self.client = TavilyClient(api_key=api_key)

    def search(self, query: str, max_results: int = 5, include_raw_content: bool = True, timeout: int = 200) -> List[SearchResult]:
        """
        Search the web using Tavily Search API
        Args:
            query: the search query
            max_results: the maximum number of results to return
            include_raw_content: whether to include the raw content of the results
            timeout: the timeout in seconds
        Returns:
            the search results
        """
        try:
            response = self.client.search(
                query = query,
                max_results = max_results,
                include_raw_content = include_raw_content,
                timeout = timeout,
            )

            results = []
            if 'results' in response:
                for item in response['results']:
                    result = SearchResult(
                        title = item.get('title', ''),
                        url = item.get('url', ''),
                        content = item.get('content', ''),
                        score = item.get('score', None),
                    )
                    results.append(result)

            return results
        except Exception as e:
            raise ValueError(f"Failed to search the web: {e}")

# singleton instance
_tavily_client = None

def get_tavily_client() -> TavilySearch:
    """
    Get the Tavily client
    """
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilySearch()
    return _tavily_client

def tavily_search(query: str, max_results: int = 5, include_raw_content: bool = True, timeout: int = 200, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search the web using Tavily Search API
    """
    try:
        if api_key:
            # use the provided API key to create a temporary client
            client = TavilySearch(api_key)
        else:
            # use the global client
            client = get_tavily_client()

        results = client.search(query, max_results, include_raw_content, timeout)
        # convert the results to a list of dictionaries
        return [result.to_dict() for result in results]

    except Exception as e:
        raise ValueError(f"Failed to search the web: {e}")

def test_search(query: str = "Test search", max_results: int =3):
    print(f"Searching for: {query}")
    print(f"Max results: {max_results}")
    try:
        results = tavily_search(query, max_results)
        if results:
            print(f"Found {len(results)} results:")
            for result in results:
                print(f"Title: {result['title']}")
                print(f"URL: {result['url']}")
                print(f"Content: {result['content'][:300]}...")
                print(f"Score: {result['score']}")
                print("-" * 50)
        else:
            print("No results found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()