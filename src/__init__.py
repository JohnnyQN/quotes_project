import os
from dotenv import load_dotenv
from flask import Flask
from src.models import db
from src.routes import routes
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_migrate import Migrate

# Load environment variables from .env file
load_dotenv()

def create_app(config_class):
    app = Flask(__name__, static_folder='static')

    # Load configuration
    app.config.from_object(config_class)

    # Ensure DATABASE_URL is set
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise ValueError("DATABASE_URL is not set. Check your environment variables.")

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    CSRFProtect(app)
    Session(app)
    CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}}, supports_credentials=True)

    # Register blueprints
    app.register_blueprint(routes)

    return app
