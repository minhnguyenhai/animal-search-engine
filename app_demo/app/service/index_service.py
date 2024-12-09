from app.utils.elastic import ElasticConnector
from typing import List, Dict, Any
import json
import os.path


class IndexService:
    def __init__(self):
        self.elastic = ElasticConnector()
        # Get the directory containing this script
        self.base_dir = os.path.dirname(os.path.abspath(__file__))


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


    def create_index(self, index_name: str):
        try:
            # Create absolute path to config file
            index_config_path = os.path.join(self.base_dir, "..", "utils", "index_config2.json")
            with open(index_config_path, "r", encoding="utf-8") as f:
                index_config = json.load(f)

            self.elastic.es.indices.create(index=index_name, body=index_config)
            return True
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {index_config_path}")
            return False
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            return False
    
    
    def set_client_index(self, index_name: str):
        try:
            self.elastic.set_index_name(index_name)
            self.elastic.update_last_updated()
            return True
        except Exception as e:
            print(f"Error setting index: {str(e)}")
            return False
        

    def post_data_to_elastic(self, index_name, list_data, upload_type='directory'):
        success = 0
        if upload_type == 'directory':
            for data in list_data:
                try:
                    name = data['name'].split('.')[0]
                    content_str = data['file_content'].decode('utf-8')
                    data_json = json.loads(content_str)

                    self.elastic.es.index(
                        index=index_name,
                        id=name,
                        body=data_json
                    )
                    success += 1
                except Exception as e:
                    print(f"Error posting data: {str(e)}")
                    pass
        else:
            try:
                content_str = list_data[0]['file_content'].decode('utf-8')
                documents = json.loads(content_str)
                
                if isinstance(documents, list):
                    for doc in documents:
                        try:
                            self.elastic.es.index(
                                index=index_name,
                                body=doc
                            )
                            success += 1
                        except Exception as e:
                            print(f"Error posting document: {str(e)}")
                            pass
                else:
                    return 0
            except Exception as e:
                print(f"Error processing bulk file: {str(e)}")
                pass
        
        return success


    def delete_index(self, index_name):
        try:
            self.elastic.es.indices.delete(index=index_name)
            return True
        except Exception as e:
            print(f"Error deleting index: {str(e)}")
            return False


    def get_index_config(self, index_name: str):
        try:
            settings = self.elastic.es.indices.get_settings(index=index_name)[index_name]["settings"]
            mappings = self.elastic.es.indices.get_mapping(index=index_name)[index_name]["mappings"]
            config = {
                "settings": settings,
                "mappings": mappings
            }
            print(f"Index config: {config}")
            return config
        except Exception as e:
            print(f"Error getting index config: {str(e)}")
            raise e