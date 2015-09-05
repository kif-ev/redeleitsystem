from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, send_file, Response
from flask.ext.login import login_required
from passlib.hash import pbkdf2_sha256

from models.database import User, Event
from models.forms import AdminUserForm, NewUserForm, NewEventForm

from shared import db, admin_permission

admin = Blueprint("admin", __name__)


@admin.route("/")
@login_required
@admin_permission.require()
def index():
    users = User.query.limit(10).all()
    events = Event.query.limit(10).all()
    return render_template("admin_index.html", users=users, events=events)

@admin.route("/user/")
@login_required
@admin_permission.require()
def user():
    users = User.query.all()
    return render_template("admin_user_index.html", users=users)

@admin.route("/user/edit", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def user_edit():
    user_id = request.args.get("id", None)
    if user_id is not None:
        user = db.session.query(User).filter_by(id=user_id).first()
        form = AdminUserForm(obj=user)
        if form.validate_on_submit():
            form.populate_obj(user)
            db.session.commit()
            return redirect(url_for(".index"))
        else:
            return render_template("admin_user_edit.html", form=form, id=user_id)
    else:
        return redirect(url_for(".index"))
            

@admin.route("/user/delete")
@login_required
@admin_permission.require()
def user_delete():
    user_id = request.args.get("id", None)
    if user_id is not None:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash("User deleted.", "alert-success")
    return redirect(url_for(".user"))

@admin.route("/user/new", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def user_new():
    form = NewUserForm()
    if form.validate_on_submit():
        password_hash = pbkdf2_sha256.encrypt(form.password.data, rounds=200000, salt_size=16)
        user = User(form.fullname.data, form.username.data, password_hash)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for(".user"))
    return render_template("admin_user_new.html", form=form)


@admin.route("/event/new", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def event_new():
    form = NewEventForm()
    if form.validate_on_submit():
        if Event.query.filter_by(name=form.name.data).count() > 0:
            flash("There already is an event with that name.", "alert-error")
            return render_template("admin_event_new.html", form=form)
        event = Event(form.name.data, form.date.data)
        db.session.add(event)
        db.session.commit()
        return redirect(url_for(".event"))
    return render_template("admin_event_new.html", form=form)

@admin.route("/event/delete")
@login_required
@admin_permission.require()
def event_delete():
    event_id = request.args.get("id", None)
    if event_id is not None:
        event  = Event.query.filter_by(id=event_id).first()
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted.", "alert-success")
    return redirect(url_for(".event"))

@admin.route("/event/edit", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def event_edit():
    event_id = request.args.get("id", None)
    if event_id is not None:
        event = db.session.query(Event).filter_by(id=event_id).first()
        form = NewEventForm(obj=event)
        if form.validate_on_submit():
            form.populate_obj(event)
            db.session.commit()
            return redirect(url_for(".index"))
        else:
            return render_template("admin_event_edit.html", form=form, id=event_id)
    else:
        return redirect(url_for(".index"))

@admin.route("/event/")
@login_required
@admin_permission.require()
def event():
    events = Event.query.all()
    print(events)
    return render_template("admin_event_index.html", events=events)
