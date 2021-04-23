from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchFormDate(FlaskForm):
    customer_id = StringField('Customer ID:', validators=[DataRequired()])
    fromDate = StringField('From Date:', validators=[DataRequired()])
    toDate = StringField('To Date:', validators=[DataRequired()])
    search = SubmitField('Search')
