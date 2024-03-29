from flask import Blueprint, redirect, url_for, request, flash, abort, send_file, Response
from flask.ext.login import login_required
from passlib.hash import pbkdf2_sha256

from datetime import datetime, timedelta

from models.database import User, Topic, Event, Speaker, Statement
from models.forms import AdminUserForm, NewUserForm, NewTopicForm, NewEventForm, AddStatementForm, EditSpeakerForm

from shared import db, admin_permission
from utils import render_layout, speaker_by_name_or_number

admin = Blueprint("admin", __name__)


@admin.route("/")
@login_required
@admin_permission.require()
def index():
    users = User.query.limit(10).all()
    events = Event.query.limit(10).all()
    return render_layout("admin_index.html", users=users, events=events)

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

@admin.route("/event/")
@login_required
@admin_permission.require()
def event():
    events = Event.query.all()
    return render_layout("admin_event_index.html", events=events)
        

@admin.route("/event/show")
@login_required
@admin_permission.require()
def event_show():
    event_id = request.args.get("id", None)
    if event_id is not None:
        event = Event.query.filter_by(id=event_id).first()
        return render_layout("admin_event_show.html", event=event)
    return redirect(url_for(".index"))


@admin.route("/event/new", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def event_new():
    form = NewEventForm()
    if form.validate_on_submit():
        if Topic.query.filter_by(name=form.name.data).count() > 0:
            flash("There already is an event with that name.", "alert-error")
            return render_layout("admin_event_new.html", form=form)
        event = Event(form.name.data)
        db.session.add(event)
        db.session.commit()
        return redirect(url_for(".event"))
    return render_layout("admin_event_new.html", form=form)


@admin.route("/event/delete")
@login_required
@admin_permission.require()
def event_delete():
    event_id = request.args.get("id", None)
    if event_id is not None:
        event = Event.query.filter_by(id=event_id).first()
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
            return render_layout("admin_event_edit.html", form=form, id=event_id)
    else:
        return redirect(url_for(".index"))


@admin.route("/topic/show")
@login_required
@admin_permission.require()
def topic_show():
    topic_id = request.args.get("id", None)
    if topic_id is not None:
        topic = Topic.query.filter_by(id=topic_id).first()
        topic.event.current_topic_id = topic.id
        db.session.commit()
        form = AddStatementForm()
        form.topic.data = topic.id
        statements = topic.sorted_statements()
        topics = topic.event.sorted_topics()
        can_undo = len(Statement.query.filter_by(executed=True, topic_id=topic_id).order_by(db.desc(Statement.execution_time)).all()) > 0
        return render_layout("admin_topic_show.html", topic=topic, form=form, statements=statements, topics=topics, can_undo_statement=can_undo)
    return redirect(url_for(".index"))
        

@admin.route("/topic/new", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def topic_new():
    event_id = request.args.get("event_id", None)
    form = NewTopicForm()
    if form.validate_on_submit():
        if Topic.query.filter_by(event_id=event_id, name=form.name.data).count() > 0:
            flash("There already is an topic with that name.", "alert-error")
            return render_layout("admin_topic_new.html", form=form)
        topic = Topic(form.name.data, form.mode.data, form.event_id.data)
        db.session.add(topic)
        db.session.commit()
        return redirect(url_for(".event_show", id=topic.event.id))
    if event_id is None:
        return redirect(url_for(".index"))
    event = Event.query.filter_by(id=event_id).first()
    form.event_id.data = event_id
    return render_layout("admin_topic_new.html", form=form, event=event)

@admin.route("/topic/delete")
@login_required
@admin_permission.require()
def topic_delete():
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
            return redirect(url_for(".topic_show", id=topic.id))
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

@admin.route("/topic/swap/up")
@login_required
@admin_permission.require()
def topic_swap_up():
    topic_id = request.args.get("id", None)
    original_id = request.args.get("original", None)
    if topic_id is not None:
        topic = Topic.query.filter_by(id=topic_id).first()
        topics = topic.event.sorted_topics()
        index = topics.index(topic)
        if index != 0:
            topic.swap_topics(topics[index-1])
            db.session.commit()
        return redirect(url_for(".topic_show", id=original_id))
    return redirect(url_for(".index"))

@admin.route("/topic/swap/down")
@login_required
@admin_permission.require()
def topic_swap_down():
    topic_id = request.args.get("id", None)
    original_id = request.args.get("original", None)
    if topic_id is not None:
        topic = Topic.query.filter_by(id=topic_id).first()
        topics = topic.event.sorted_topics()
        index = topics.index(topic)
        if index != len(topics) - 1:
            topic.swap_topics(topics[index+1])
            db.session.commit()
        return redirect(url_for(".topic_show", id=original_id))
    return redirect(url_for(".index"))

@admin.route("/speaker/rename", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def speaker_edit():
    #speaker = Speaker.query.filter_by(number=number,event).first()
    #if speaker is not None:
    #id=statement.speaker.identifier(), topic_id=topic.id)
    speaker_id = request.args.get("id", None)
    topic_id = request.args.get("topic_id", None)
    speaker = Speaker.query.filter_by(id=speaker_id).first()
    form = EditSpeakerForm(obj=speaker)
    form.topic_id.data=topic_id
    
    if speaker is not None:
        if form.validate_on_submit():
            speaker.name = form.name.data
            speaker.number = form.number.data
            db.session.commit()
            return redirect(url_for(".topic_show",id=form.topic_id.data))
        else: 
            return render_layout("admin_speaker_edit.html", form=form, speaker=speaker, topic_id=topic_id)
    else:
        return redirect(url_for(".index"))
    


@admin.route("/statement/")
@login_required
@admin_permission.require()
def statement():
    statements = Statement.query.all()
    return render_layout("admin_statement_index.html", statement=statement)

@admin.route("/statement/new", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def statement_new():
    form = AddStatementForm()
    if form.validate_on_submit():
        statement = request.form.get("submit","add_statement")
        topic = Topic.query.filter_by(id=form.topic.data).first()
        speaker = speaker_by_name_or_number(form.speaker_name.data, topic.event.id)
        if topic is not None and speaker is not None:
            if speaker.count_active(topic) == 0 or (statement == "add_meta_statement" 
                and speaker.count_active_meta(topic) == 0) :
                statement = Statement(speaker.id, topic.id,
                                      is_meta=(statement == "add_meta_statement"),
                                      is_current=(not topic.sorted_statements()))
                db.session.add(statement)
                db.session.commit()
            return redirect(url_for(".topic_show", id=topic.id))
    return render_layout("admin_statement_new.html", form=form)

@admin.route("/statement/done")
@login_required
@admin_permission.require()
def statement_done():
    statement_id = request.args.get("id", None)
    if statement_id is not None:
        statement = Statement.query.filter_by(id=statement_id).first()
        if statement is not None:
            statement.done()
            db.session.commit()
    topic_id = request.args.get("topic_id", None)
    if topic_id is not None:
        return redirect(url_for(".topic_show", id=topic_id))
    return redirect(url_for(".index"))

@admin.route("/statement/delete")
@login_required
@admin_permission.require()
def statement_delete():
    statement_id = request.args.get("id", None)
    topic_id = request.args.get("topic_id", None)
    if statement_id is not None:
        statement = Statement.query.filter_by(id=statement_id).first()
        if statement is not None:
            topic = Topic.query.filter_by(id=topic_id).first()
            if len(topic.sorted_statements()) > 1: 
                topic.sorted_statements()[1].is_current = True
            db.session.delete(statement)
            db.session.commit()
    if topic_id is not None:
        return redirect(url_for(".topic_show", id=topic_id))
    return redirect(url_for(".index"))

@admin.route("/statement/undo")
@login_required
@admin_permission.require()
def statement_undo():
    topic_id = request.args.get("topic_id", None)
    if topic_id is not None:
        statement = Statement.query.filter_by(executed=True, topic_id=topic_id).order_by(db.desc(Statement.execution_time)).first()
        statement.undo()
        db.session.commit()
    return redirect(url_for(".topic_show", id=topic_id))

@admin.route("/pause", methods=["GET", "POST"])
@login_required
@admin_permission.require()
def pause():
    event_id = request.args.get("id", None)
    if event_id is not None:
        event = Event.query.filter_by(id=event_id).first()
        if event is not None:
            if event.paused_until == None:
                event.paused_until = datetime(1970, 1, 1)
            event.paused = not event.paused
            if event.paused:
                rawtime = float(request.form["timeslider"])
                delta = timedelta(seconds=rawtime)
                print(delta)
                event.paused_until = datetime.now() + delta    
            db.session.commit()
    topic_id = request.args.get("original", None)
    return redirect(url_for(".topic_show", id=topic_id))
