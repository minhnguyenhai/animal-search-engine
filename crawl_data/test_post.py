import json
import os
from elasticsearch import Elasticsearch

def post_to_elasticsearch(file_path):
    # Khởi tạo Elasticsearch client
    es = Elasticsearch([{
        'scheme': 'http',
        'host': 'localhost', 
        'port': 9200
    }])
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                file_name = os.path.basename(file_path)
                # Đẩy dữ liệu vào Elasticsearch
                es.index(index='animal_information', 
                        id=file_name.split('.')[0], 
                        body=data)
                return True, f'Đã đẩy dữ liệu vào Elasticsearch: {file_name}'
            except json.JSONDecodeError:
                return False, f'Không thể đọc file: {file_name}'
    except Exception as e:
        return False, f'Lỗi: {str(e)}'

# Chạy trực tiếp
if __name__ == "__main__":
    # Đọc danh sách các file JSON trong thư mục content
    for file_name in os.listdir('crawl_data/content_final'):
        if file_name.endswith('.json'):
            file_path = f'crawl_data/content_final/{file_name}'
            success, message = post_to_elasticsearch(file_path)
            print(message)


