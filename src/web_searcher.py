import requests
from typing import List, Dict, Optional
from config.settings import SERPER_API_KEY, MAX_SEARCH_RESULTS


class WebSearcher:
    def __init__(self, api_key: Optional[str] = SERPER_API_KEY):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"

    def search(self, query: str, num_results: int = MAX_SEARCH_RESULTS) -> List[Dict]:
        """
        Search the web using Serper API.

        Args:
            query (str): Search query
            num_results (int): Max results to fetch

        Returns:
            List of dicts containing 'title', 'snippet', 'link', 'source'
        """
        if not self.api_key:
            print("[WebSearcher] Missing SERPER_API_KEY")
            return []

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {"q": query, "num": num_results}

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            organic_results = data.get("organic", [])
            return [
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", ""),
                    "source": "web",
                }
                for item in organic_results
            ]

        except requests.RequestException as e:
            print(f"[WebSearcher] Request error: {e}")
        except ValueError:
            print("[WebSearcher] Failed to parse JSON response")

        return []

    def format_results(self, results: List[Dict]) -> str:
        """
        Format search results into a string suitable for LLM input.
        """
        if not results:
            return "No web search results found."

        formatted = "### Web Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result['title']}**\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   Source: {result['link']}\n\n"

        return formatted
