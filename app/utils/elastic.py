
from elasticsearch import Elasticsearch

class ElasticConnector:
    def __init__(self):
        # Try to connect with HTTPS first, fallback to HTTP if needed
        try:
            self.es = Elasticsearch(
                ['https://localhost:9200'],  # Replace with your actual Elasticsearch host
                verify_certs=False,  # For development only, set to True in production
                ssl_show_warn=False
            )
        except Exception as e:
            # Fallback to HTTP
            self.es = Elasticsearch(
                ['http://localhost:9200']  # Replace with your actual Elasticsearch host
            )
        
        if not self.es.ping():
            raise ConnectionError("Could not connect to Elasticsearch")