from src import app, db
from src.models import User, Quote, Vote, Report, Category  

with app.app_context():
    db.create_all()  # Creates all tables in the database
    # Optional: Initialize predefined categories
    initialize_categories()
