from flask import Blueprint

search = Blueprint("search", __name__)
admin = Blueprint("admin", __name__)
from app.routes.searchRoutes import perform_search
from app.routes.adminRoutes import admin_dashboard, get_indexes, create_index, upload_data, set_client_index