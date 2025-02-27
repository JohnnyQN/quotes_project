import os
import sys
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  

# Load environment variables
load_dotenv()

# Importing the create_app function from factory pattern
from src import create_app
from src.models import db

# Create the app instance using the factory function
app = create_app()

# Initialize Flask-Migrate
migrate = Migrate(app, db)  # Ensure Flask-Migrate is properly initialized

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import and start the scheduler if it's not already running
from src.tasks import scheduler

if not scheduler.running:
    scheduler.start()
    logger.info("Background scheduler started.")

# Debugging info
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

# Run the app in development mode
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
