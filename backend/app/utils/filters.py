from flask import current_app as app
from dataclasses import dataclass
import requests


@dataclass
class SearchResult:
    id: int
    title: str
    description: str
    url: str


class SearchFilters:
    def __init__(self, index):
        self.url = f"{app.config['ELASTICSEARCH_URL']}/{index}/_search"
        self.headers = {
            "Content-Type": "application/json"
        }
        
        
    def search_by_query_string(self, query):
        payload = {
            "query": {
                "query_string": {
                    "analyze_wildcard": True,
                    "query": query,
                    "fields": ["title", "description", "content"]
                }
            },
            "size": 10
        }
        
        response = requests.get(
            self.url, 
            headers=self.headers, 
            json=payload
        )
        
        search_results = []
        
        if response.status_code == 200:
            data = response.json()
            data_results = data["hits"]["hits"]
            
            for result_id, data_result in enumerate(data_results, start=1):
                result = SearchResult(
                    id=result_id,
                    title=data_result["_source"]["title"],
                    description=data_result["_source"]["description"],
                    url=data_result["_source"]["url"]
                )
                
                search_results.append(result)
 
        return search_results