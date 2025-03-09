import sys
import os
import json  
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.models import db, Quote, Category
from src import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_import_app():
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': os.getenv("SECRET_KEY")
    })
    return app

def main():
    app = create_import_app()
    with app.app_context():
        try:
            with open('bulk_quotes.json', 'r') as file:
                quotes_data = json.load(file)
        except FileNotFoundError:
            print("Error: bulk_quotes.json not found.")
            sys.exit(1)
        except json.JSONDecodeError:
            print("Error: Invalid JSON in bulk_quotes.json.")
            sys.exit(1)

        for item in quotes_data.get('quotes', []):
            text = item.get('text')
            author = item.get('author', 'Unknown')
            category_name = item.get('category', 'Uncategorized')

            # Find or create the category
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)

            # Avoid duplicate quotes
            existing_quote = Quote.query.filter_by(text=text).first()
            if not existing_quote:
                new_quote = Quote(text=text, author=author)
                new_quote.categories.append(category)
                db.session.add(new_quote)

        db.session.commit()
        print("Quotes imported successfully!")

if __name__ == "__main__":
    main()
