from typing import List, Dict, Any
from config import Config
from elasticsearch import Elasticsearch


class ElasticConnector:
    """Mở kết nối với Elasticsearch."""
    def __init__(self):
        """Khởi tạo kết nối với Elasticsearch."""
        self.es = Elasticsearch(
            Config.ELASTICSEARCH_URL,
            http_auth=(Config.ELASTICSEARCH_USERNAME , Config.ELASTICSEARCH_PASSWORD)
        )

    
