import os
import time
import logging
from dotenv import load_dotenv
from flask import Flask
from src.models import db
from src.routes import routes
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from flask_migrate import Migrate
from src.config import config_options
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Load environment variables from .env file
load_dotenv()

def create_app(config_name=None):
    """Application factory function."""
    app = Flask(__name__, static_folder='static')

    # Set default config to 'development' if not specified
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    
    # Load configuration from our config_options dictionary
    app.config.from_object(config_options.get(config_name, config_options["default"]))
    
    # Ensure SQLALCHEMY_DATABASE_URI is set
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise ValueError("DATABASE_URL is not set. Check your environment variables.")
    
    # Enable query recording for slow query logging
    app.config["SQLALCHEMY_RECORD_QUERIES"] = True

    # Measure database initialization time
    start_db_time = time.time()
    db.init_app(app)
    db_time = time.time() - start_db_time
    print(f"Database Init Time: {db_time:.5f} seconds")

    Migrate(app, db)
    CSRFProtect(app)
    Session(app)
    CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}}, supports_credentials=True)

    # Register our blueprints
    app.register_blueprint(routes)

    # Log slow SQL queries using SQLAlchemy event listeners
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        total_time = time.time() - conn.info["query_start_time"].pop(-1)
        if total_time >= 0.5:  # Log queries that take 0.5 seconds or longer
            app.logger.warning(f"SLOW QUERY: {statement} (Took {total_time:.2f}s)")

    return app

# Ensure that app runs with correct configurations
if __name__ == "__main__":
    env = os.getenv("FLASK_ENV", "development")
    config_class = config_options.get(env, config_options["default"])
    app = create_app(config_class)
    app.run(debug=True)
