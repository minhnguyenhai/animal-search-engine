from flask import request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
from app.routes import admin
from app.service.index_service import IndexService

index_service = IndexService()

uploaded_files = {}  # Dictionary to store uploaded files by index

@admin.route('/')
def admin_dashboard():
    return render_template('admin.html')


@admin.route('/indexes', methods=['GET'])
def get_indexes():
    return jsonify(index_service.get_indexes())
    

@admin.route('/create-index', methods=['POST'])
def create_index():
    data = request.get_json()
    index_name = data.get('indexName')
    if index_name is None:
        return jsonify({
            "error": "Missing required fields.",
            "message": "The required parameter 'indexName' is missing."
        }), 400
    is_created = index_service.create_index(index_name)
    if is_created:
        return jsonify({
            "message": f"Index {index_name} created."
        })
    else:
        return jsonify({
            "error": "Internal server error.",
            "message": "Failed to create index."
        }), 500
    


@admin.route('/upload-data/<index_name>', methods=['POST'])
def upload_data(index_name):
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files provided"}), 400
            
        files = request.files.getlist('files')
        file_data = []

        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file_content = file.read()
                file_data.append({
                    'name': filename,
                    'file_content': file_content
                })
        
        num_of_success = index_service.post_data_to_elastic(index_name,file_data)
        
        return jsonify({
            "message": f"Đẩy thành công {num_of_success} / {len(file_data)} lên {index_name}"
        })

    except Exception as e:
        print(e)
        return jsonify({
            "error": "Upload failed",
            "message": str(e)
        }), 500


@admin.route('/set-client-index', methods=['POST'])
def set_client_index():
    try:
        #get index_name from form data
        index_name = request.form['index']
        if index_name is None:
            return jsonify({
                "error": "Missing required fields.",
                "message": "The required parameter 'index' is missing."
            }), 400
        is_set = index_service.set_client_index(index_name)
        if is_set:
            return jsonify({
                "message": f"Index set to {index_name}"
            })
        else:
            return jsonify({
                "error": "Internal server error.",
                "message": "Failed to set index."
            }), 500
        
    except Exception as e:
        print(e)
        return jsonify({
            "error": "Internal server error.",
            "message": str(e)
        }), 500


@admin.route('/delete-index/<index_name>', methods=['DELETE'])
def delete_index(index_name):
    try:
        is_deleted = index_service.delete_index(index_name)
        if is_deleted:
            return jsonify({
                "message": f"Index {index_name} deleted."
            })
        else:
            return jsonify({
                "message": "Failed to delete index."
            })
    except Exception as e:
        print(e)
        return jsonify({
            "error": "Internal server error.",
            "message": str(e)
        }), 500


@admin.route('/index-config/<index_name>', methods=['GET'])
def get_index_config(index_name):
    try:
        config = index_service.get_index_config(index_name)
        return jsonify(config)
    except Exception as e:
        return jsonify({
            "error": "Internal server error.",
            "message": str(e)
        }), 500

