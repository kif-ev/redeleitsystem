#!/usr/bin/env python3

from flask import Flask, g, current_up, request, render_template, session, flash, redirect, url_for, abort
from flask.ext.login import login_user, logout_user, login_required, current_user
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed, identity_loaded, UserNeed, RoleNeed
from passlib.hash import pbkdf2_sha256

import config
from shared import db, login_manager
from models.forms import LoginForm
from models.database import User

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "alert-error"

Principal(app)

from modules import admin

app.register_blueprint(admin.admin, url_prefix="/admin")
db.create_all(app=app)

@app.route("/")
def index():
    if not len(db.session.query(User).all()) > 0:
        fullname = input("Fullname for admin user:")
        username = input("Username for admin user:")
        password = pbkdf2_sha256.encrypt(input("Password for admin user:"), rounds=200000, salt_size=16)
        user = User(fullname, username, password, ["admin", "user"])
        db.session.add(user)
        db.session.commit()
    return render_template("index.html")


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user
    
    # Add the UserNeed to the identity
    if hasattr(current_user, "id"):
        identity.provides.add(UserNeed(current_user.id))
    
    # Assuming the User Model has a list of roles, update the identity
    # with the roles that the user provides
    if hasattr(current_user, "roles") and current_user.roles is not None:
        for role in current_user.roles:
            identity.provides.add(RoleNeed(role))

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter_by(id=user_id).first()

if __name__ == "__main__":
    app.run(debug=config.DEBUG)
