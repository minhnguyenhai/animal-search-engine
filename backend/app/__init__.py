from flask import Flask
from dotenv import load_dotenv
from config import Config


def create_app(config_class=Config):
    # Load environment variables from .env
    # load_dotenv()
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    from app.search import search as search_bp
    app.register_blueprint(search_bp)
    
    return app