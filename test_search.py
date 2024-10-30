from elasticsearch import Elasticsearch
import json
# Kết nối đến Elasticsearch
es = Elasticsearch("http://localhost:9200")

def create_query(user_input):
    # Bỏ từ "động vật" khỏi truy vấn nếu có
    user_input = user_input.replace("động vật", "").strip()
    
    terms = user_input.split()
    # gộp 2 từ liền kề thành 1 từ
    for i in range(len(terms) - 1):
        terms[i] = terms[i] + " " + terms[i + 1]
    terms = terms[:-1]
    
    # Tạo các truy vấn con với trọng số
    queries = []
    weight = 1  # Khởi đầu trọng số nhỏ nhất
    
    for term in terms:  # Từ phía sau có trọng số cao hơn
        # Thêm từng từ vào danh sách queries với trọng số tăng dần
        queries.append({
            "match": {
                "description": {
                    "query": term,
                    "boost": weight
                }
            }
        })
        weight += 1

    # Gộp tất cả các truy vấn con thành một truy vấn bool
    query = {
        "size": 10,
        "query": {
            "bool": {
                "should": queries
            }
        }
    }
    
    return query

# Nhập truy vấn từ bàn phím
user_input = input("Nhập truy vấn của bạn: ")
query = create_query(user_input)
#in ra raw query
print("Raw query:")
print(json.dumps(query, indent=4))
# Thực hiện truy vấn
response = es.search(index="animal_information", body=query)

# In kết quả
print("Kết quả truy vấn:")
for hit in response['hits']['hits']:
    print(f"{hit['_source']['title']} ({hit['_score']})")
    print(hit['_source']['description'])
    print()
