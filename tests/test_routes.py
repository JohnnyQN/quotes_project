import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import create_app, db

@pytest.fixture
def test_client():
    app = create_app({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for tests
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_home_route(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Quotes" in response.data  

def test_login_invalid(test_client):
    response = test_client.post('/login', data={'username': 'wronguser', 'password': 'wrongpass'}, follow_redirects=True)
    assert b"Invalid username or password." in response.data  

def test_upvote_without_login(test_client):
    response = test_client.post('/vote/1', follow_redirects=True)
    assert b"You need to be logged in to vote." in response.data 

def test_signup_password_strength(test_client):
    response = test_client.post('/signup', data={'username': 'newuser', 'email': 'test@example.com', 'password': 'a'}, follow_redirects=True)
    # Ensure that form errors are flashed
    assert b"Password must be at least 8 characters long." in response.data, response.data
