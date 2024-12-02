from dataclasses import dataclass
from app.utils.elastic import ElasticConnector
from typing import List, Dict, Any
from urllib.parse import unquote

@dataclass
class SearchResult:
    title: str
    description: str
    url: str
    score: float

class SearchService:
    MAX_RESULTS = 10
    MIN_SCORE_THRESHOLD = 0.1

    def __init__(self):
        self.elastic = ElasticConnector().es
        self.index_name = ElasticConnector().index_name

    def create_query(self, search_text: str) -> Dict[str, Any]:
        search_text = search_text.lower()
        cleaned_text = search_text
        
        return {
            "query": {
                "multi_match": {
                    "query": cleaned_text,
                    "fields": [
                        "title^1",
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

    def search_query(self, query: str) -> List[SearchResult]:
        query_body = self.create_query(query)
        try:
            response = self.elastic.search(index=self.index_name, body=query_body)
        except Exception as e:
            print(f"Error searching: {str(e)}")
            return []
        
        title_could_be = ["title", "scientific_name", "Title", "song", "tenchude", "content"]
        description_could_be = ["description", "Description", "content", "noidung", "Content"]
        url_could_be = ["url", "link"]

        def find_first_match(source: dict, fields: list, default: str) -> str:
            for field in fields:
                if value := source.get(field):
                    return value
            return default

        return [SearchResult(
            find_first_match(hit["_source"], title_could_be, "không xác định được tiêu đề"),
            find_first_match(hit["_source"], description_could_be, "không xác định được mô tả"),
            unquote(find_first_match(hit["_source"], url_could_be, "không xác định được đường dẫn")),
            hit["_score"]
        ) for hit in response["hits"]["hits"]]
    
    def count_index(self):  # Fixed typo in method name
        return self.elastic.count(self.index_name)





