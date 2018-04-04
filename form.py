
from flask_wtf import Form
from wtforms import StringField, PasswordField,SelectField
from wtforms.validators import DataRequired, Email

class EmailForm(Form):
    email = StringField('Email', validators=[DataRequired(), Email()])

class PasswordForm(Form):
    password = PasswordField('Password', validators=[DataRequired()])

class BookSearchForm(Form):
    choices = [('Title', 'Title'),
               ('Author', 'Author'),
               ('Department', 'Department'),
               ('Course', 'Course'),
               ('ISBN', 'ISBN')]
    select = SelectField('Search for book:', choices=choices)
    search = StringField('')