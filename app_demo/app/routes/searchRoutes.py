from flask import  request, jsonify
from app.routes import search
from app.service.search_service import SearchService
import logging

@search.route("/search", methods=["GET"])
def perform_search():  # renamed from 'search' to avoid conflict
    try:
        query = request.args.get("q")
        
        if query is None:
            return jsonify({
                "error": "Missing required fields.",
                "message": "The required parameter 'q' is missing."
            }), 400

        if query.strip() == "":
            return jsonify({
                "error": "Invalid query",
                "message": "The query cannot be empty."
            }), 400
        
        search_results = SearchService().search_query(query)
        
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                'title': result.title,
                'url': result.url,
                'description': result.description
            })
        
        return jsonify(formatted_results)
    
    except Exception as e:
        logging.error(f"Search error: {str(e)}")  # Add logging
        return jsonify({
            "error": "Internal server error.",
            "message": str(e)
        }), 500