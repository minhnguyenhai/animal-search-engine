from app.utils.elastic import ElasticConnector
from typing import List, Dict, Any
import json



class IndexService:
    def __init__(self):
        self.elastic = ElasticConnector()


    def get_indexes(self) -> List[Dict[str, Any]]:
        user_index = []
        try:
            # Add last used index
            user_index.append({
                "name": f"{self.elastic.index_name}",
                "count": 0
            })
            
            indices = self.elastic.es.indices.get_alias(index="*")
            indices = list(indices.keys())
            
            for index in indices:
                if not index.startswith("."):
                    # Get document count for the index
                    count = self.elastic.es.cat.count(index=index, format="json")
                    doc_count = int(count[0]["count"])
                    
                    user_index.append({
                        "name": index,
                        "count": doc_count
                    })
            return user_index
        except Exception as e:
            print(f"Error getting indexes: {str(e)}")
            return []

    
    def set_client_index(self, index_name: str):
        try:
            self.elastic.set_index_name(index_name)
            self.elastic.update_last_updated()
            return True
        except Exception as e:
            print(f"Error setting index: {str(e)}")
            return False
        

    def post_data_to_elastic(self, index_name, list_data):
        success=0
        for data in list_data:
            try:
                name = data['name'].split('.')[0]
                # Decode byte string to UTF-8 and parse JSON
                content_str = data['file_content'].decode('utf-8')
                data_json = json.loads(content_str)

                self.elastic.es.index(
                    index=index_name,
                    id=name,
                    body=data_json
                )
                success+=1
            
            except Exception as e:
                print(f"Error posting data: {str(e)}")
                pass
        return success


    def delete_index(self, index_name):
        try:
            self.elastic.es.indices.delete(index=index_name)
            return True
        except Exception as e:
            print(f"Error deleting index: {str(e)}")
            return False