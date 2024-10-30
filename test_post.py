#tôi cần đọc danh sách các file  json trong thư mục content sau đó đẩy các json này lên elasticsearch
import json
import os
from elasticsearch import Elasticsearch

# Khởi tạo Elasticsearch client
es = Elasticsearch([{
    'scheme': 'http',
    'host': 'localhost', 
    'port': 9200
    }])

# Đọc danh sách các file JSON trong thư mục content
for file_name in os.listdir('crawl_data/content_final'):
    if file_name.endswith('.json'):
        with open(f'crawl_data/content_final/{file_name}', 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                print(f'Không thể đọc file: {file_name}')
                continue
            # Đẩy dữ liệu vào Elasticsearch, id là số dứng trước dấu . ví dụ 123. Hổ là 123
            es.index(index='animal_information', id=file_name.split('.')[0], body=data)
            print(f'Đã đẩy dữ liệu vào Elasticsearch: {file_name}')
            

