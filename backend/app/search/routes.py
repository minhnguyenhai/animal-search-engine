from flask import request
from app.search import search
from app.utils.filters import SearchFilters


search_filters = SearchFilters(index="")


@search.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query")
    
    search_results = search_filters.search_by_query_string(query)
    
    return search_results