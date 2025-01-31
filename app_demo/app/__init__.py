from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from config import Config


def create_app(config_class=Config):
    # Load environment variables from .env
    # load_dotenv()
    
    app = Flask(__name__, static_folder="static")
    CORS(app)  # Thêm dòng này
    app.config.from_object(config_class)
    
    from app.routes import search as search_bp
    from app.routes import admin as admin_bp
    app.register_blueprint(search_bp)
    app.register_blueprint(admin_bp,url_prefix="/admin")

    
    return app