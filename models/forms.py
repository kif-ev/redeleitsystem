from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField, SelectField, DateField, IntegerField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo, Email, Optional, Length, NumberRange, AnyOf
from models.database import User

import shared


class LoginForm(Form):
    username = StringField("Username", validators=[InputRequired("Entering your username is required.")])
    password = PasswordField("Password", validators=[InputRequired("Entering your password is required.")])
    remember_me = BooleanField("Remember me?")

class NewUserForm(Form):
    fullname = StringField("Full name", validators=[InputRequired("Entering your name is required.")])
    username = StringField("Username", validators=[InputRequired("Entering your username is required.")])
    password = PasswordField("Password", validators=[InputRequired("Entering your password is required.")])
    confirm = PasswordField("Repeat Password", validators=[InputRequired("Entering your password is required."), EqualTo("password", message="Your passwords must match.")])

class AdminUserForm(Form):
    fullname = StringField("Full name", validators=[InputRequired("Entering the name is required.")])
    username = StringField("Username", validators=[InputRequired("Entering the username is required.")])
    roles = SelectMultipleField("User roles", choices=[(x.lower().strip(), x) for x in shared.roles])

class AddStatementForm(Form):
    speaker_name = StringField("Speaker", validators=[InputRequired("Entering the speaker is required.")])
