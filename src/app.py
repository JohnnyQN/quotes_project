import os
import sys
import logging
from dotenv import load_dotenv
from flask_migrate import Migrate  
from flask_caching import Cache  # Import Flask-Caching

# Load environment variables
load_dotenv()

# Import configurations
from src import create_app
from src.models import db, Quote  # Ensure Quote model is imported
from src.config import config_options

# Determine environment and create app instance
env = os.getenv("FLASK_ENV", "default")
config_class = config_options.get(env, config_options["default"])
app = create_app(config_class)

# Initialize Flask-Migrate
migrate = Migrate(app, db)  

# Initialize Flask-Caching
cache = Cache(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debugging info
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")

# Determine the port
port = int(os.environ.get("PORT", 10000)) 
logger.info(f"Starting app on port {port}")

# Caching Expensive Queries
@cache.cached(timeout=600, key_prefix="all_quotes")
def get_all_quotes():
    """Retrieve all quotes from the database with caching"""
    return Quote.query.all()

@cache.cached(timeout=600, key_prefix="categorized_quotes")
def get_categorized_quotes():
    """Retrieve categorized quotes with caching"""
    categorized_quotes = {}
    quotes = Quote.query.filter(Quote.category.isnot(None)).all()
    for quote in quotes:
        if quote.category not in categorized_quotes:
            categorized_quotes[quote.category] = []
        categorized_quotes[quote.category].append(quote)
    return categorized_quotes

@cache.cached(timeout=600, key_prefix="uncategorized_quotes")
def get_uncategorized_quotes():
    """Retrieve uncategorized quotes with caching"""
    return Quote.query.filter(Quote.category.is_(None)).all()

# Run the app in development mode
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
