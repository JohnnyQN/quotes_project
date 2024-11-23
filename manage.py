from flask.cli import FlaskGroup
from src import create_app
from src.models import db

app = create_app()
cli = FlaskGroup(app)

if __name__ == '__main__':
    cli()