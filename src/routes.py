from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import time
from src.models import db, User, Quote, Vote, Report, Category
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from src.services import get_quote_of_the_day, get_categorized_quotes, get_uncategorized_quotes
from src.forms import QuoteForm, SignupForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

routes = Blueprint('routes', __name__)

@routes.route('/')
@cross_origin()
def home():
    start_time = time.time()
    personalized_quotes = []
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            personalized_quotes = Quote.query.options(joinedload(Quote.categories)).join(Quote.categories).filter(
                Category.id.in_([c.id for c in user.categories])
            ).all()
        else:
            logger.error(f"No user found with ID: {session['user_id']}")
    else:
        logger.warning("No user is logged in.")

    categorized_quotes = get_categorized_quotes()
    uncategorized_quotes = get_uncategorized_quotes()

    logger.debug("Home route accessed.")
    logger.debug(f"Categorized Quotes Retrieved: {categorized_quotes}")
    logger.debug(f"Uncategorized Quotes Retrieved: {uncategorized_quotes}")
    logger.debug(f"Personalized Quotes Retrieved: {personalized_quotes}")

    featured_qod = get_quote_of_the_day()
    community_qod = Quote.query.filter_by(is_community_qod=True).first()

    logger.debug(f"Home route execution time: {time.time() - start_time:.5f} seconds")

    return render_template(
        'index.html',
        categorized_quotes=categorized_quotes,
        uncategorized_quotes=uncategorized_quotes,
        community_qod=community_qod,
        featured_qod=featured_qod,
        personalized_quotes=personalized_quotes
    )

@routes.before_app_request
def debug_csrf_token():
    if request.endpoint in ['routes.signup', 'routes.new_quote']:
        logger.debug(f"CSRF Token (from cookie): {request.cookies.get('csrf_token')}")
        logger.debug(f"CSRF Token (from form): {request.form.get('csrf_token')}")

@routes.route('/signup', methods=["GET", "POST"])
@cross_origin()
def signup():
    start_time = time.time()
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'warning')
            return redirect(url_for('routes.signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'warning')
            return redirect(url_for('routes.signup'))
        password_hash = generate_password_hash(password)
        new_user = User(email=email, username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        logger.debug(f"Signup route execution time: {time.time() - start_time:.5f} seconds")
        return redirect(url_for('routes.login'))
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'danger')
    return render_template('signup.html', form=form)

@routes.route('/login', methods=["GET", "POST"])
@cross_origin()
def login():
    start_time = time.time()
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
        session.modified = True
        flash('Login successful!', 'success')
        logger.debug(f"Login route execution time: {time.time() - start_time:.5f} seconds")
        return redirect(url_for('routes.home'))
    return render_template('login.html')

@routes.route('/logout')
@cross_origin()
def logout():
    start_time = time.time()
    user_id = session.pop('user_id', None)
    logger.info(f"User {user_id} logged out")
    flash('You have been logged out.', 'success')
    logger.debug(f"Logout route execution time: {time.time() - start_time:.5f} seconds")
    return redirect(url_for('routes.home'))

@routes.route('/quotes', methods=["GET"])
@cross_origin()
def view_quotes():
    logger.debug("View quotes page accessed.")
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '').strip()

    # Use eager loading to avoid N+1 queries
    if search_query:
        all_quotes = Quote.query.options(joinedload(Quote.categories)).join(
            User, User.id == Quote.submitted_by, isouter=True
        ).filter(
            (Quote.text.ilike(f"%{search_query}%")) |
            (Quote.author.ilike(f"%{search_query}%")) |
            (User.username.ilike(f"%{search_query}%"))
        ).order_by(Quote.id).all()
    else:
        all_quotes = Quote.query.options(joinedload(Quote.categories)).order_by(Quote.id).all()

    categorized_quotes = {}
    uncategorized_quotes = []
    for quote in all_quotes:
        if quote.categories:
            for cat in quote.categories:
                cat_name = cat.name.strip().lower()
                categorized_quotes.setdefault(cat_name, []).append(quote)
        else:
            uncategorized_quotes.append(quote)

    sorted_categories = dict(sorted(categorized_quotes.items()))
    category_list = list(sorted_categories.items())
    total_categories = len(category_list)
    total_pages = (total_categories // per_page) + (1 if total_categories % per_page != 0 else 0)
    if uncategorized_quotes:
        total_pages += 1
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_categories = category_list[start_index:end_index]
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
        search_query=search_query,
        expanded_categories=request.args.get('expanded_categories', '').split(',')
    )

@routes.route('/quotes/new', methods=["GET", "POST"])
@cross_origin()
def new_quote():
    form = QuoteForm()
    form.categories.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
        logger.debug("New quote form submitted.")
        if 'user_id' not in session:
            logger.warning("User must be logged in to submit a quote.")
            flash('You need to be logged in to submit a quote.', 'warning')
            return redirect(url_for('routes.login'))
        new_quote_obj = Quote(
            text=form.text.data,
            author=form.author.data,
            submitted_by=session['user_id']
        )
        db.session.add(new_quote_obj)
        if form.categories.data:
            selected_cats = Category.query.filter(Category.id.in_(form.categories.data)).all()
            new_quote_obj.categories.extend(selected_cats)
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
        selected_cats = Category.query.filter(Category.id.in_(selected_category_ids)).all()
        user.categories = selected_cats
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
                logger.info(f"User {user_id} clicked the same vote type. Removing vote.")
                if vote_type == 'upvote':
                    quote.upvotes -= 1
                elif vote_type == 'downvote':
                    quote.downvotes -= 1
                db.session.delete(existing_vote)
                flash('Vote removed successfully.', 'info')
            else:
                logger.info(f"User {user_id} changed vote from {existing_vote.vote_type} to {vote_type}.")
                if existing_vote.vote_type == 'upvote':
                    quote.upvotes -= 1
                elif existing_vote.vote_type == 'downvote':
                    quote.downvotes -= 1
                existing_vote.vote_type = vote_type
                if vote_type == 'upvote':
                    quote.upvotes += 1
                elif vote_type == 'downvote':
                    quote.downvotes += 1
                flash('Vote updated successfully!', 'success')
        db.session.commit()
        logger.info(f"Vote successfully updated for quote ID {quote_id}")
        expanded_categories = request.form.get('expanded_categories', '')
        page = request.form.get('page', 1)
        search_query = request.form.get('search', '')
        next_page = request.referrer or url_for('routes.view_quotes',
                                               page=page,
                                               search=search_query,
                                               expanded_categories=expanded_categories)
        return redirect(next_page + f"#quote-{quote_id}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error occurred during voting process: {str(e)}")
        flash('An error occurred while processing your vote. Please try again.', 'danger')
        return redirect(request.referrer or url_for('routes.home'))
