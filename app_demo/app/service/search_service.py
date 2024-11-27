from dataclasses import dataclass
from app.utils.elastic import ElasticConnector
from typing import List, Dict, Any
from urllib.parse import unquote

@dataclass
class SearchResult:
    title: str
    description: str
    url: str

class SearchService:
    MAX_RESULTS = 10
    MIN_SCORE_THRESHOLD = 0.1

    def __init__(self):
        self.elastic = ElasticConnector().es

    def create_query(self, search_text: str) -> Dict[str, Any]:
        search_text = search_text.lower()
        cleaned_text = search_text
        
        return {
            "query": {
                "multi_match": {
                    "query": cleaned_text,
                    "fields": [
                        "title^2",
                        "description^2", 
                        "content^0.5",
                        "classify^1",
                        "categories^2"
                    ],
                    "type": "best_fields"
                }
            },
            "size": self.MAX_RESULTS,
            "min_score": self.MIN_SCORE_THRESHOLD
        }

    def search_query(self, query: str,index_name="animal_information") -> List[SearchResult]:
        query_body = self.create_query(query)
        try:
            response = self.elastic.search(index=index_name, body=query_body)
        except Exception as e:
            print(f"Error searching: {str(e)}")
            return []
        
        return [SearchResult(
            hit["_source"]["title"],
            hit["_source"]["description"],
            unquote(hit["_source"]["url"])
        ) for hit in response["hits"]["hits"]]




