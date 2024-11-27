from dataclasses import dataclass
from app.utils.elastic import ElasticConnector
from typing import List, Dict, Any
from urllib.parse import unquote



class IndexService:
    def __init__(self):
        self.elastic = ElasticConnector().es


    def create_index(self, index_name: str, mapping: Dict[str, Any]) -> bool:
        try:
            self.elastic.indices.create(index=index_name, body=mapping)
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            return False
        
        return True