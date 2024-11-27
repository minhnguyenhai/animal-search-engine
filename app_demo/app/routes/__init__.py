from flask import Blueprint

search = Blueprint("search", __name__)
admin = Blueprint("admin", __name__)
from app.routes.searchRoutes import perform_search