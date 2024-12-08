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

    def _has_vietnamese_diacritics(self, text: str) -> bool:
        vietnamese_diacritics = "áàảãạâấầẩẫậăắằẳẵặóòỏõọôốồổỗộơớờởỡợéèẻẽẹêếềểễệúùủũụưứừửữựíìỉĩịýỳỷỹỵđ"
        return any(char in text for char in vietnamese_diacritics)

    def create_query(self, search_text: str) -> Dict[str, Any]:
        search_text = search_text.lower()
        cleaned_text = search_text #.replace("động vật", "").replace("dong vat", "").strip()
        
        if not self._has_vietnamese_diacritics(cleaned_text):
            # Query for non-accented text - prioritize no_accent fields
            return {
                "query": {
                    "multi_match": {
                        "query": cleaned_text,
                        "fields": [
                            "title.no_accent^2",
                            "description.no_accent^3",
                            "content.no_accent^1",
                            "classify.no_accent^2",
                            "categories.no_accent^3",
                            "title^0.5",
                            "description^0.8",
                            "content^0.3",
                            "classify^0.5",
                            "categories^0.8"
                        ],
                        "type": "best_fields"
                    }
                },
                "size": self.MAX_RESULTS,
                "min_score": self.MIN_SCORE_THRESHOLD
            }
        
        # Query for accented text - prioritize original fields
        return {
            "query": {
                "multi_match": {
                    "query": cleaned_text,
                    "fields": [
                        "title^2",
                        "description^3",
                        "content^1",
                        "classify^2",
                        "categories^3",
                        "title.no_accent^0.5",
                        "description.no_accent^0.8",
                        "content.no_accent^0.3",
                        "classify.no_accent^0.5",
                        "categories.no_accent^0.8"
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





