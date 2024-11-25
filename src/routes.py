from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from src.models import db, User, Quote, Vote, Report, Category
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from src.services import get_quote_of_the_day, fetch_multiple_quotes_from_api, get_categorized_quotes, get_uncategorized_quotes
from src.forms import QuoteForm, SignupForm  
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

routes = Blueprint('routes', __name__)

@routes.route('/')
@cross_origin()
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        # Fetch personalized quotes based on user's preferred categories
        personalized_quotes = Quote.query.join(Quote.categories).filter(Category.id.in_([c.id for c in user.categories])).all()
    else:
        personalized_quotes = []

    # Consolidate categories
    consolidate_categories()

    categorized_quotes = get_categorized_quotes()
    uncategorized_quotes = get_uncategorized_quotes()
    logger.debug("Home route accessed.")
    logger.debug(f"Categorized Quotes Retrieved: {categorized_quotes}")
    logger.debug(f"Uncategorized Quotes Retrieved: {uncategorized_quotes}")
    logger.debug(f"Personalized Quotes Retrieved: {personalized_quotes}")

    featured_qod = get_quote_of_the_day()
    community_qod = Quote.query.filter_by(is_community_qod=True).first()

    logger.info("Rendering home page with featured, community, and personalized quotes")
    return render_template(
        'index.html', 
        categorized_quotes=categorized_quotes,
        uncategorized_quotes=uncategorized_quotes,
        community_qod=community_qod,
        featured_qod=featured_qod,
        personalized_quotes=personalized_quotes
    )


def consolidate_categories():
    try:
        # Define mapping of categories to consolidate
        category_mapping = {
            'inspire': 'Inspiration',
            'management': 'Management',
            'sports': 'Sports',
            'life': 'Life',
            'funny': 'Humor',
            'students': 'Education',
            'hardwork': 'Hard Work',
            'self-improvement': 'Self Improvement',
            'self-worth': 'Self Worth',
            'self-imposed-limits': 'Self Imposed Limits',
            # Add more mappings as needed
        }

        # Fetch all categories
        all_categories = Category.query.all()
        category_names = {category.name.lower(): category for category in all_categories}

        for old_name, new_name in category_mapping.items():
            old_name = old_name.lower()
            new_name = new_name.strip()

            # Check if old category exists and new category does not cause conflict
            if old_name in category_names and new_name.lower() not in category_names:
                category = category_names[old_name]
                category.name = new_name
                logger.info(f"Updating category '{old_name}' to '{new_name}'")
            elif old_name in category_names and new_name.lower() in category_names:
                # Merge quotes from old category to new category
                old_category = category_names[old_name]
                new_category = category_names[new_name.lower()]
                for quote in old_category.quotes:
                    if quote not in new_category.quotes:
                        new_category.quotes.append(quote)
                # Delete the old category after merging
                db.session.delete(old_category)
                logger.info(f"Merging category '{old_name}' into '{new_name}' and deleting '{old_name}'")

        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Error consolidating categories: {str(e)}")

@routes.before_app_request
def debug_csrf_token():
    if request.endpoint in ['routes.signup', 'routes.new_quote']:
        logger.debug(f"CSRF Token (from cookie): {request.cookies.get('csrf_token')}")
        logger.debug(f"CSRF Token (from form): {request.form.get('csrf_token')}")

@routes.route('/signup', methods=["GET", "POST"])
@cross_origin()
def signup():
    form = SignupForm()
    if request.method == "POST" and form.validate_on_submit():
        # Log the CSRF token
        logger.debug(f"Received CSRF token: {request.form.get('csrf_token')}")

        logger.debug("Signup form submitted.")
        
        # Retrieve the email, username, and password from the form
        email = form.email.data
        username = form.username.data
        password = form.password.data

        # Validate email field is provided
        if not email:
            flash('Email is required.', 'danger')
            return redirect(url_for('routes.signup'))

        # Check if the username or email already exists
        if User.query.filter_by(username=username).first():
            logger.warning(f"Attempt to create a user with existing username: {username}")
            flash('Username already exists.', 'warning')
            return redirect(url_for('routes.signup'))
        
        if User.query.filter_by(email=email).first():
            logger.warning(f"Attempt to create a user with existing email: {email}")
            flash('Email already exists.', 'warning')
            return redirect(url_for('routes.signup'))

        # Hash the password and create a new user
        password_hash = generate_password_hash(password)
        new_user = User(email=email, username=username, password_hash=password_hash)
        
        # Add the new user to the database
        db.session.add(new_user)
        db.session.commit()

        logger.info(f"New user created: {username}")
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('routes.login'))

    return render_template('signup.html', form=form)

@routes.route('/login', methods=["GET", "POST"])
@cross_origin()
def login():
    if request.method == "POST":
        logger.debug("Login form submitted.")
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            logger.warning(f"Login failed for username: {username}")
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('routes.login'))

        session['user_id'] = user.id
        logger.info(f"User {username} logged in")
        flash('Login successful!', 'success')
        return redirect(url_for('routes.home'))

    return render_template('login.html')

@routes.route('/logout')
@cross_origin()
def logout():
    user_id = session.pop('user_id', None)
    logger.info(f"User {user_id} logged out")
    flash('You have been logged out.', 'success')
    return redirect(url_for('routes.home'))

@routes.route('/quotes', methods=["GET"])
@cross_origin()
def view_quotes():
    logger.debug("View quotes page accessed.")

    # Get pagination parameters from the request
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)  # Number of categories per page

    # Fetch and group all quotes by category
    categorized_quotes = {}
    uncategorized_quotes = []

    all_quotes = Quote.query.order_by(Quote.id).all()

    # Group quotes by categories and collect uncategorized quotes
    for quote in all_quotes:
        if quote.categories:
            for category in quote.categories:
                category_name = category.name.strip().lower()
                if category_name not in categorized_quotes:
                    categorized_quotes[category_name] = []
                categorized_quotes[category_name].append(quote)
        else:
            uncategorized_quotes.append(quote)

    # Sort categories alphabetically
    sorted_categories = dict(sorted(categorized_quotes.items()))

    # Create a list of tuples (category_name, quotes) for easier pagination
    category_list = list(sorted_categories.items())

    # Calculate the total number of pages, considering uncategorized quotes at the end
    total_categories = len(category_list)
    total_pages = (total_categories // per_page) + (1 if total_categories % per_page != 0 else 0)
    if uncategorized_quotes:
        total_pages += 1

    # Apply pagination to the list of categories
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_categories = category_list[start_index:end_index]

    # Determine if we are on the last page to show uncategorized quotes
    show_uncategorized = (page == total_pages) and uncategorized_quotes

    logger.info("Rendering view quotes page with grouped quotes by categories.")
    return render_template(
        'view_quotes.html',
        paginated_categories=paginated_categories,
        uncategorized_quotes=uncategorized_quotes if show_uncategorized else [],
        total_categories=total_categories,
        total_pages=total_pages,
        page=page,
        per_page=per_page,
        search_query=request.args.get('search', ''),
        expanded_categories=request.args.get('expanded_categories', '').split(',')
    )

@routes.route('/quotes/new', methods=["GET", "POST"])
@cross_origin()
def new_quote():
    form = QuoteForm()
    form.categories.choices = [(category.id, category.name) for category in Category.query.all()]

    if form.validate_on_submit():
        logger.debug("New quote form submitted.")
        
        if 'user_id' not in session:
            logger.warning("User must be logged in to submit a quote.")
            flash('You need to be logged in to submit a quote.', 'warning')
            return redirect(url_for('routes.login'))

        new_quote = Quote(text=form.text.data, author=form.author.data, submitted_by=session['user_id'])
        db.session.add(new_quote)

        # Associate categories with the quote
        if form.categories.data:
            selected_categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
            new_quote.categories.extend(selected_categories)

        db.session.commit()

        logger.info("New quote submitted successfully.")
        flash('Quote submitted successfully!', 'success')
        return redirect(url_for('routes.view_quotes'))

    logger.debug("Rendering new quote form.")
    return render_template('submit_quote.html', form=form)

@routes.route('/preferences', methods=["GET", "POST"])
@cross_origin()
def preferences():
    if 'user_id' not in session:
        logger.warning("Attempt to access preferences without logging in.")
        flash('You need to be logged in to set preferences.', 'warning')
        return redirect(url_for('routes.login'))

    user = User.query.get(session['user_id'])
    categories = Category.query.all()

    if not categories:
        logger.debug("No categories available, rendering an empty form.")
        return render_template('preferences.html', user=user, categories=categories)

    if request.method == "POST":
        logger.debug("Preferences form submitted.")
        selected_category_ids = request.form.getlist('categories')
        selected_categories = Category.query.filter(Category.id.in_(selected_category_ids)).all()

        user.categories = selected_categories
        db.session.commit()

        logger.info("User preferences updated.")
        flash('Your preferences have been updated.', 'success')
        return redirect(url_for('routes.home'))

    logger.debug("Rendering preferences form.")
    return render_template('preferences.html', user=user, categories=categories)

@routes.route('/vote/<int:quote_id>', methods=["POST"])
@cross_origin()
def vote_quote(quote_id):
    logger.debug(f"Vote request received for quote ID {quote_id}")
    if 'user_id' not in session:
        logger.warning("User must be logged in to vote.")
        flash('You need to be logged in to vote.', 'danger')
        return redirect(url_for('routes.login'))

    try:
        user_id = session['user_id']
        vote_type = request.form.get('vote_type')

        if not vote_type:
            logger.error("Invalid vote type provided.")
            flash('Invalid vote type.', 'danger')
            return redirect(request.referrer or url_for('routes.home'))

        quote = Quote.query.get_or_404(quote_id)
        logger.info(f"Updating vote for quote ID {quote_id}")

        existing_vote = Vote.query.filter_by(user_id=user_id, quote_id=quote_id).first()

        if not existing_vote:
            logger.debug(f"Creating new Vote: User ID {user_id}, Quote ID {quote_id}, Vote Type {vote_type}")
            new_vote = Vote(user_id=user_id, quote_id=quote_id, vote_type=vote_type)
            db.session.add(new_vote)

            if vote_type == 'upvote':
                quote.upvotes += 1
            elif vote_type == 'downvote':
                quote.downvotes += 1
            flash('Vote added successfully!', 'success')

        else:
            if existing_vote.vote_type == vote_type:
                # User clicked the same vote type, remove the vote
                logger.info(f"User {user_id} clicked the same vote type. Removing vote for quote ID {quote_id}.")
                if vote_type == 'upvote':
                    quote.upvotes -= 1
                elif vote_type == 'downvote':
                    quote.downvotes -= 1
                db.session.delete(existing_vote)
                flash('Vote removed successfully.', 'info')

            else:
                # User changed vote type
                logger.info(f"User {user_id} already voted on quote ID {quote_id}. Updating vote.")
                if existing_vote.vote_type == 'upvote':
                    quote.upvotes -= 1
                elif existing_vote.vote_type == 'downvote':
                    quote.downvotes -= 1

                # Update vote type
                existing_vote.vote_type = vote_type

                # Adjust counts
                if vote_type == 'upvote':
                    quote.upvotes += 1
                elif vote_type == 'downvote':
                    quote.downvotes += 1
                flash('Vote updated successfully!', 'success')

        # Commit changes to the database
        db.session.commit()
        logger.info(f"Vote successfully updated for quote ID {quote_id}")

        # Redirect to the previous page or specified next page, keeping all parameters intact
        expanded_categories = request.form.get('expanded_categories', '')
        page = request.form.get('page', 1)
        search_query = request.form.get('search', '')

        next_page = request.referrer or url_for('routes.view_quotes', page=page, search=search_query, expanded_categories=expanded_categories)
        return redirect(next_page + f"#quote-{quote_id}")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error occurred during voting process: {str(e)}")
        flash('An error occurred while processing your vote. Please try again.', 'danger')
        return redirect(request.referrer or url_for('routes.home'))
