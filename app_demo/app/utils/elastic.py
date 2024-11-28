from typing import List, Dict, Any
from config import Config
from elasticsearch import Elasticsearch
import json
from datetime import datetime
import os

# Get absolute path for settings file
current_dir = os.path.dirname(os.path.abspath(__file__))
setting_path = os.path.join(current_dir, 'elastic_setting.json')

# Default settings
default_setting = {
    "last_used_index": "animals",
    "last_updated": None
}

# Try to load settings or create default
try:
    with open(setting_path, "r") as f:
        setting = json.load(f)
except FileNotFoundError:
    setting = default_setting
    with open(setting_path, "w") as f:
        json.dump(setting, f)

class ElasticConnector:
    """Mở kết nối với Elasticsearch."""
    def __init__(self):
        """Khởi tạo kết nối với Elasticsearch."""
        self.es = Elasticsearch(
            Config.ELASTICSEARCH_URL,
            http_auth=(Config.ELASTICSEARCH_USERNAME , Config.ELASTICSEARCH_PASSWORD)
        )
        self.index_name = setting["last_used_index"]
        self.last_updated=setting["last_updated"]

    def set_index_name(self, index_name: str):
        """Set index name."""
        self.index_name = index_name
        setting["last_used_index"] = index_name
        json.dump(setting, open(setting_path, "w"))

    def update_last_updated(self):
        """Update last updated."""
        self.last_updated = str(datetime.now())
        setting["last_updated"] = self.last_updated
        json.dump(setting, open(setting_path, "w"))
