from typing import List, Dict, Any
from elasticsearch import Elasticsearch

class SearchEngine:
    """Handles search operations using Elasticsearch."""
    
    ELASTICSEARCH_URL = "http://localhost:9200"
    INDEX_NAME = "animal_information"
    MIN_SCORE_THRESHOLD = 1
    MAX_RESULTS = 10
    
    def __init__(self):
        """Initialize Elasticsearch connection."""
        self.es = Elasticsearch(self.ELASTICSEARCH_URL)
    
    def create_query(self, search_text: str) -> Dict[str, Any]:
        """
        Create an Elasticsearch query from user input using the full search text.

        Args:
            search_text: The user's search text

        Returns:
            Dict containing the Elasticsearch query structure
        """
        #chuyển về chữ thường
        search_text = search_text.lower()
        # Remove "động vật" and clean up input
        cleaned_text = search_text.replace("động vật", "").strip()
        
        query = {
            "query": {
                "multi_match": {
                    "query": cleaned_text,
                    "fields": ["title", "description", "content", "url"],
                    "type": "best_fields"
                }
            },
            "size": self.MAX_RESULTS,
            "min_score": self.MIN_SCORE_THRESHOLD
        }

        return query

    def search(self, search_text: str) -> List[Dict[str, Any]]:
        """
        Execute search query and return filtered results.
        
        Args:
            search_text: The user's search text
            
        Returns:
            List of search results above score threshold
        """
        query = self.create_query(search_text)
        response = self.es.search(index=self.INDEX_NAME, body=query)
        
        return [
            {
                'title': hit['_source'].get('title', 'N/A'),
                'description': hit['_source'].get('description', 'No description'),
                'url': hit['_source'].get('url', '#'),
                'score': hit['_score']
            }
            for hit in response['hits']['hits']
            if hit['_score'] > self.MIN_SCORE_THRESHOLD
        ]
