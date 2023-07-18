from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators, IntegerField, SubmitField


class LoginForm(FlaskForm):
    username = StringField('Username: ', [validators.InputRequired()])
    password = PasswordField('Password: ', [validators.InputRequired()])
    submit = SubmitField("Login")

class CreateAccount(FlaskForm):
    username = StringField("Username: ", [validators.InputRequired()])
    email = StringField("Email: ", [validators.InputRequired()])
    password = PasswordField("Password: ", [validators.InputRequired()])
    submit = SubmitField("Create Account")