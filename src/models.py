import datetime
from flask_sqlalchemy import SQLAlchemy
import logging


db = SQLAlchemy()

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Models

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    quotes = db.relationship('Quote', backref='user', lazy=True)
    votes = db.relationship('Vote', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)
    categories = db.relationship('Category', secondary='user_preferences', back_populates='users')

    def __init__(self, username, email, password_hash):
        logger.debug(f"Creating new User: {username}, {email}")
        self.username = username
        self.email = email
        self.password_hash = password_hash


class Quote(db.Model):
    __tablename__ = 'quotes'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=True)
    date_fetched = db.Column(db.Date, nullable=False, default=datetime.date.today)
    submitted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_community_qod = db.Column(db.Boolean, default=False)
    is_featured_qod = db.Column(db.Boolean, default=False)
    report_count = db.Column(db.Integer, default=0)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)

    votes = db.relationship('Vote', backref='quote', lazy=True)
    reports = db.relationship('Report', backref='quote', lazy=True)
    categories = db.relationship('Category', secondary='quote_categories', back_populates='quotes')

    def __init__(self, text, author, date_fetched=None, submitted_by=None, is_community_qod=False, is_featured_qod=False):
        logger.debug(f"Creating new Quote: {text} by {author}")
        self.text = text
        self.author = author
        self.date_fetched = date_fetched if date_fetched else datetime.date.today()
        self.submitted_by = submitted_by
        self.is_community_qod = is_community_qod
        self.is_featured_qod = is_featured_qod

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    vote_type = db.Column(db.String, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'quote_id', name='unique_user_quote_vote'),
    )

    def __init__(self, user_id, quote_id, vote_type):
        logger.debug(f"Creating new Vote: User ID {user_id}, Quote ID {quote_id}, Vote Type {vote_type}")
        self.user_id = user_id
        self.quote_id = quote_id
        self.vote_type = vote_type


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quote_id = db.Column(db.Integer, db.ForeignKey('quotes.id'))
    report_reason = db.Column(db.String, nullable=True)
    report_date = db.Column(db.Date, default=datetime.date.today)

    def __init__(self, user_id, quote_id, report_reason):
        logger.debug(f"Creating new Report: User ID {user_id}, Quote ID {quote_id}, Reason: {report_reason}")
        self.user_id = user_id
        self.quote_id = quote_id
        self.report_reason = report_reason


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    users = db.relationship('User', secondary='user_preferences', back_populates='categories')
    quotes = db.relationship('Quote', secondary='quote_categories', back_populates='categories')

    def __init__(self, name):
        logger.debug(f"Creating new Category: {name}")
        self.name = name


user_preferences = db.Table('user_preferences',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

quote_categories = db.Table('quote_categories',
    db.Column('quote_id', db.Integer, db.ForeignKey('quotes.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

# Function to initialize predefined categories
def initialize_categories():
    predefined_categories = [
        "inspire", "management", "sports", "life", "funny", "love", "art", "students"
    ]
    for category_name in predefined_categories:
        existing_category = Category.query.filter_by(name=category_name).first()
        if not existing_category:
            new_category = Category(name=category_name)
            db.session.add(new_category)
            logger.debug(f"Added predefined category: {category_name}")
    db.session.commit()
