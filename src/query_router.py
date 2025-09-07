from typing import Literal
from config.settings import WEB_SEARCH_KEYWORDS


class QueryRouter:
    def __init__(self):
        self.web_search_keywords = [kw.lower() for kw in WEB_SEARCH_KEYWORDS]

    def route_query(
        self, query: str, has_documents: bool = True
    ) -> Literal["document", "web", "hybrid"]:
        """
        Route query based on content and available documents.

        Returns:
            - "document": Search only in uploaded documents
            - "web": Search only on the web
            - "hybrid": Use both docs and web
        """
        query_lower = query.lower().strip()

        # If no documents available, force web search
        if not has_documents:
            return "web"

        # Count keyword matches
        web_indicators = sum(
            1 for keyword in self.web_search_keywords if keyword in query_lower
        )

        # Decision logic
        if web_indicators >= 2:
            return "web"
        elif web_indicators == 1:
            return "hybrid"
        else:
            return "document"

    def should_use_web(self, query: str) -> bool:
        """
        Quick boolean check if web search should be used
        (at least one keyword match).
        """
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.web_search_keywords)
