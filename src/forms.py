from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Regexp

class QuoteForm(FlaskForm):
    text = StringField('Quote Text', validators=[DataRequired()])
    author = StringField('Author', default='Unknown')
    categories = SelectMultipleField('Categories', coerce=int)
    submit = SubmitField('Submit')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField(
        'Password', 
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters long.")]
    )
    submit = SubmitField('Sign Up')
