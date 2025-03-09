import json
import os
from src.models import db, Quote, Category
from src import create_app

# Initialize the Flask app
app = create_app()

# Load quotes from the JSON file
base_dir = os.path.dirname(os.path.abspath(__file__)) 
file_path = os.path.join(base_dir, "bulk_quotes.json")

with open(file_path, "r") as f:
    quotes_data = json.load(f)["quotes"]  

with app.app_context():
    # Step 1: Extract unique categories
    category_names = set(quote["category"] for quote in quotes_data)  

    # Step 2: Insert categories into the database if they don't exist
    for name in category_names:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))

    db.session.commit()
    print(f"✅ {len(category_names)} categories added!")

    # Step 3: Insert quotes and associate them with categories
    for quote in quotes_data:
        text = quote["text"]  
        author = quote.get("author", "Unknown")  
        category_name = quote["category"]

        # Get category object
        category = Category.query.filter_by(name=category_name).first()

        # Check if quote already exists before inserting
        if not Quote.query.filter_by(text=text).first(): 
            new_quote = Quote(text=text, author=author)  

            if category:
                new_quote.categories.append(category) 

            db.session.add(new_quote)

    db.session.commit()
    print(f"✅ {len(quotes_data)} quotes added successfully!")
