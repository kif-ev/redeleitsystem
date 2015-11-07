from flask import Blueprint, redirect, url_for, request, flash, abort, send_file, Response
from flask.ext.login import login_required
from passlib.hash import pbkdf2_sha256

from models.database import User, Topic
from models.forms import AdminUserForm, NewUserForm, NewTopicForm

from shared import db, admin_permission, render_layout

admin = Blueprint("admin", __name__)


@admin.route("/")
@login_required
@admin_permission.require()
def index():
    users = User.query.limit(10).all()
    topics = Topic.query.limit(10).all()
    return render_layout("admin_index.html", users=users, topics=topics)

@admin.route("/user/")
@login_required
@admin_permission.require()
def user():
    users = User.query.all()
    return render_layout("admin_user_index.html", users=users)

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
            return render_layout("admin_user_edit.html", form=form, id=user_id)
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
    return render_layout("admin_user_new.html", form=form)


@admin.route("/topic/new", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def topic_new():
    form = NewTopicForm()
    if form.validate_on_submit():
        if Topic.query.filter_by(name=form.name.data).count() > 0:
            flash("There already is an topic with that name.", "alert-error")
            return render_layout("admin_topic_new.html", form=form)
        topic = Topic(form.name.data, form.mode.data)
        db.session.add(topic)
        db.session.commit()
        return redirect(url_for(".topic"))
    return render_layout("admin_topic_new.html", form=form)

@admin.route("/topic/delete")
@login_required
@admin_permission.require()
def topc_delete():
    topic_id = request.args.get("id", None)
    if topic_id is not None:
        topic  = Topic.query.filter_by(id=topic_id).first()
        db.session.delete(topic)
        db.session.commit()
        flash("Topic deleted.", "alert-success")
    return redirect(url_for(".topic"))

@admin.route("/topic/edit", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def topic_edit():
    topic_id = request.args.get("id", None)
    if topic_id is not None:
        topic = db.session.query(Topic).filter_by(id=topic_id).first()
        form = NewTopicForm(obj=topic)
        if form.validate_on_submit():
            form.populate_obj(topic)
            db.session.commit()
            return redirect(url_for(".index"))
        else:
            return render_layout("admin_topic_edit.html", form=form, id=topic_id)
    else:
        return redirect(url_for(".index"))

@admin.route("/topic/")
@login_required
@admin_permission.require()
def topic():
    topics = Topic.query.all()
    return render_layout("admin_topic_index.html", topics=topics)
