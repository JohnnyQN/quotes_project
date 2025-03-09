import datetime
import time
import requests
import os
import logging
from collections import defaultdict
from sqlalchemy.orm import joinedload
from src.models import db, Quote, Category

logger = logging.getLogger(__name__)

# Function to get the quote of the day
def get_quote_of_the_day():
    start_time = time.time()
    today = datetime.date.today()
    quote = Quote.query.filter_by(date_fetched=today, is_featured_qod=True).first()
    if quote:
        logger.info("Returning existing quote of the day from database.")
        return quote
    logger.info("No quote of the day found for today. Fetching a new one.")
    fetched_quote = fetch_new_quote_from_api(today)
    elapsed_time = time.time() - start_time
    logger.info(f"get_quote_of_the_day execution time: {elapsed_time:.5f} seconds")
    return fetched_quote

# Function to fetch a new quote from the API
def fetch_new_quote_from_api(today):
    start_time = time.time()
    logger.info("Attempting to fetch a new quote from the API.")
    api_url = "https://quotes.rest/qod?language=en"
    headers = {
        "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if "contents" in data and "quotes" in data["contents"]:
            new_quote = data["contents"]["quotes"][0]
            category_name = new_quote.get("category", "Uncategorized")
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name)
                db.session.add(category)
                db.session.commit()
            quote = Quote(
                text=new_quote["quote"],
                author=new_quote["author"],
                date_fetched=today,
                is_featured_qod=True
            )
            quote.categories.append(category)
            db.session.add(quote)
            db.session.commit()
            logger.info("Fetched and saved new quote of the day.")
            elapsed_time = time.time() - start_time
            logger.info(f"fetch_new_quote_from_api execution time: {elapsed_time:.5f} seconds")
            return quote
        else:
            logger.warning("No quote found in API response, creating default quote.")
            return create_default_quote(today)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching quote: {e}")
        return create_default_quote(today)

# Function to create a default quote
def create_default_quote(today):
    logger.info("Creating a default quote.")
    default_quote = Quote(
        text="This is a default quote as we couldn't fetch a quote today.",
        author="Admin",
        date_fetched=today,
        is_featured_qod=True
    )
    db.session.add(default_quote)
    db.session.commit()
    logger.info("Created and saved default quote of the day.")
    return default_quote

# Function to fetch multiple quotes from the API
def fetch_multiple_quotes_from_api(total_quotes=500):
    logger.info(f"Attempting to fetch {total_quotes} quotes from the API.")
    quotes_fetched = 0
    batch_size = 1  # Reducing batch size to avoid potential rate limit issues
    max_attempts = 5  # Stop if we are rate limited this many times
    rate_limit_count = 0

    while quotes_fetched < total_quotes:
        api_url = f"https://quotes.rest/quote/random?language=en&limit={batch_size}"
        headers = {
            "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
            "Accept": "application/json"
        }

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "contents" in data and "quotes" in data["contents"]:
                for new_quote in data["contents"]["quotes"]:
                    category_name = new_quote.get("category", "Uncategorized")

                    # Fetch or create the category in the database
                    category = Category.query.filter_by(name=category_name).first()
                    if not category:
                        category = Category(name=category_name)
                        db.session.add(category)
                        db.session.commit()

                    # Check if the quote already exists to avoid duplicates
                    existing_quote = Quote.query.filter_by(text=new_quote["quote"]).first()
                    if not existing_quote:
                        # Create a new quote and associate it with the category
                        quote = Quote(
                            text=new_quote["quote"],
                            author=new_quote["author"]
                        )
                        quote.categories.append(category)  # Associate the quote with the category
                        db.session.add(quote)
                        db.session.commit()
                        quotes_fetched += 1
                        logger.info(f"Fetched and saved quote: {new_quote['quote'][:30]}...")

            # If we fetched fewer quotes than expected, break to avoid infinite loops
            if quotes_fetched >= total_quotes:
                break

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 429:
                rate_limit_count += 1
                logger.error(f"Rate limit reached: {http_err}. Stopping further attempts after {rate_limit_count} limit hits.")
                if rate_limit_count >= max_attempts:
                    logger.error(f"Rate limit reached {rate_limit_count} times. Aborting further requests.")
                    break
            else:
                logger.error(f"HTTP error occurred: {http_err}")
                break
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching quotes: {e}")
            break

        # Adding delay to reduce the chance of getting rate-limited
        time.sleep(3600)  

    logger.info(f"Total quotes fetched: {quotes_fetched}")
    return quotes_fetched

# Function to fetch categories from the API
def fetch_categories_from_api():
    api_url = "https://quotes.rest/qod/categories?language=en&detailed=false"
    headers = {
        "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "contents" in data and "categories" in data["contents"]:
            categories = data["contents"]["categories"]

            if isinstance(categories, dict):
                logger.info("Categories fetched successfully from API.")
                return [{'name': key, 'title': value} for key, value in categories.items()]
        logger.warning("No categories found in API response.")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching categories: {e}")
        return []

# Function to get categorized quotes
def get_categorized_quotes():
    start_time = time.time()
    categorized_quotes = defaultdict(list)
    quotes = Quote.query.options(joinedload(Quote.categories)).all()
    for quote in quotes:
        for category in quote.categories:
            normalized_category = category.name.strip().lower()
            categorized_quotes[normalized_category].append(quote)
    logger.info(f"Total categorized quotes count: {len(categorized_quotes)}")
    elapsed_time = time.time() - start_time
    logger.info(f"get_categorized_quotes execution time: {elapsed_time:.5f} seconds")
    return dict(categorized_quotes)

# Function to get uncategorized quotes
def get_uncategorized_quotes():
    start_time = time.time()
    uncategorized_quotes = Quote.query.filter(~Quote.categories.any()).all()
    logger.info(f"Total uncategorized quotes count: {len(uncategorized_quotes)}")
    elapsed_time = time.time() - start_time
    logger.info(f"get_uncategorized_quotes execution time: {elapsed_time:.5f} seconds")
    return uncategorized_quotes

