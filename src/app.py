import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  

# Load environment variables
load_dotenv()

# Import configurations
from src import create_app
from src.models import db
from src.config import DevelopmentConfig, ProductionConfig

# Determine environment and create app instance
env = os.getenv("FLASK_ENV", "development")
config_class = DevelopmentConfig if env == "development" else ProductionConfig
app = create_app(config_class)

# Initialize Flask-Migrate
migrate = Migrate(app, db)  

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import and start the scheduler if it's not already running
# from src.tasks import scheduler

# if not scheduler.running:
#     scheduler.start()
#     logger.info("Background scheduler started.")

# Debugging info
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")

# Determine the port
port = int(os.environ.get("PORT", 10000)) 
logger.info(f"Starting app on port {port}")

# Run the app in development mode
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
