#!/usr/bin/env python3

from flask import Flask, g, current_app, request, session, flash, redirect, url_for, abort
from flask.ext.login import login_user, logout_user, login_required, current_user
from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed, identity_loaded, UserNeed, RoleNeed
from passlib.hash import pbkdf2_sha256

import config
from shared import db, login_manager, render_layout
from models.forms import LoginForm, NewUserForm
from models.database import User, Statement, Speaker, Event

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "alert-error"

Principal(app)

from modules import admin, speech

app.register_blueprint(admin.admin, url_prefix="/admin")
app.register_blueprint(speech.speech, url_prefix="/speech")
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
    events = Event.query.all()
    meta = []
    for event in events:
        ls = [ (statement, speaker, count) for (statement, speaker, count) in speech.query_statements("pending", event.id) if not statement.executed ]
        no_speaker = Speaker("No Speaker", event)
        no_statement = Statement(no_speaker, event)
        meta.append((ls[0] if len(ls) > 0 else (no_statement, no_speaker, ()), event))
    return render_layout("index.html", meta=meta)

@app.route("/update")
def update():
    events = Event.query.all()
    meta = []
    for event in events:
        ls = [ (statement, speaker, count) for (statement, speaker, count) in speech.query_statements("pending", event.id) if not statement.executed ]
        no_speaker = Speaker("No Speaker", event)
        no_statement = Statement(no_speaker, event)
        meta.append((ls[0] if len(ls) > 0 else (no_statement, no_speaker, ()), event))
    return render_layout("content_index.html", meta=meta)

@app.route("/update.js")
def update_js():
    update_interval = config.UPDATE_INDEX_INTERVAL or 1
    div = "rede-content-div"
    target_url = url_for(".update")
    return render_layout("update.js", update_interval=update_interval, div=div, target=target_url)

@app.route("/update_time")
def update_time():
    return render_layout("content_time.html")

@app.route("/update_time.js")
def update_time_js():
    update_interval = config.UPDATE_TIME_INTERVAL or 10
    div = "rede-time-div"
    target_url = url_for("update_time")
    return render_layout("update.js", update_interval=update_interval, div=div, target_url=target_url)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter_by(username=form.username.data).first()
        if (user is not None) and (pbkdf2_sha256.verify(form.password.data, user.password)):
            login_user(user, remember=form.remember_me.data)
            identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
            flash("Welcome back, {}!".format(user.fullname), "alert-success")
            return redirect(request.args.get("next") or url_for(".index"))
        else:
            flash("Invalid username or wrong password", "alert-error")
    return render_layout("login.html", form=form)

@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    for key in ("identity.name", "identiy.auth_type"):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())
    flash("You have been logged out.", "alert-success")
    return redirect(url_for(".index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = NewUserForm()
    if form.validate_on_submit():
        length = len(db.session.query(User).filter_by(username=form.username.data).all())
        if length > 0:
            flash("There already is a user with that name.")
            return render_layout("register.html", form=form)
        password = pbkdf2_sha256.encrypt(form.password.data, rounds=200000, salt_size=16)
        user = User(fullname, username, password, [])
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created, you may now log in with it.")
        return redirect(url_for(".login"))
    return render_layout("register.html", form=form)

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
