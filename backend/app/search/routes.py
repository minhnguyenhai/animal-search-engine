from flask import request, jsonify
from app.search import search
from app.utils.filters import SearchFilters


@search.route("/search", methods=["POST"])
def search():
    try:
        data = request.get_json()
        
        if data is None:
            raise ValueError("Invalid JSON data.")
        
        query = data.get("query")
        
        if query is None:
            return jsonify({
                "error": "Missing required fields.",
                "message": "The required fields 'query' are missing."
            }), 400

        if query.strip() == "":
            return jsonify({
                "error": "Invalid query",
                "message": "The 'query' field cannot be empty."
            }), 400
        
        search_filters = SearchFilters(index="animal_sources")
        search_results = search_filters.search_by_query_string(query)
        
        return jsonify({
            "search_results": search_results
        })
    
    except ValueError as e:
        return jsonify({
            "error": "Invalid data.",
            "message": str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            "error": "Internal server error.",
            "message": str(e)
        }), 500