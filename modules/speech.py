from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, send_file, Response
from flask.ext.login import login_required

from models.database import User, Statement, Speaker, Event
from models.forms import AddStatementForm

from shared import db, admin_permission, user_permission

from datetime import datetime
import json

speech = Blueprint("speech", __name__)

def transpose(arr):
    print(list)
    return list(map(list, zip(*arr)))

def query_statements(mode, event_id):
    statements = []
    if mode == "pending":
        statements = db.session.query(Statement, Speaker, db.func.count(Statement.speaker).label("total")).group_by(Speaker.id).join(Speaker).filter(Statement.event == event_id).order_by("total ASC", Statement.insertion_time).all()
    elif mode == "all":
        statements = db.session.query(Statement, Speaker).join(Speaker).filter(Statement.event == event_id).order_by(Statement.insertion_time).all()
    elif mode == "past":
        statements = db.session.query(Statement, Speaker).join(Speaker).filter(Statement.executed == True).filter(Statement.event == event_id).order_by(Statement.execution_time).all()
    return statements

@speech.route("/index")
def index():
    mode = request.args.get("mode", "pending")
    event_id = request.args.get("event", None) 
    meta = []
    if event_id is not None and event_id != "-1":
        event = Event.query.filter_by(id=event_id).first()
        form = AddStatementForm()
        form.event.data = event.id
        meta.append((query_statements(mode, event_id), form, event))
    else:
        for event in Event.query.all():
            form = AddStatementForm()
            form.event.data = event.id
            meta.append((query_statements(mode, event.id), form, event))
        event_id = -1
    return render_template("speech_index.html", meta=meta, event_id=event_id)

@speech.route("/show")
def show():
    mode = request.args.get("mode", "pending") 
    event_id = request.args.get("event", None)
    meta = []
    if event_id is not None and event_id is not "-1":
        event = Event.query.filter_by(id=event_id).first()
        meta.append((query_statements(mode, event_id), event))
    else:
        for event in Event.query.all():
            meta.append((query_statements(mode, event.id), event))
    return render_template("speech_show.html", mode=mode, meta=meta, event_id=event_id)

@speech.route("/update")
def update():
    mode = request.args.get("mode", "pending") 
    event_id = request.args.get("event", None)
    meta = []
    if event_id is not None and event_id != "-1":
        event = Event.query.filter_by(id=event_id).first()
        meta.append((query_statements(mode, event_id), event))
    else:
        for event in Event.query.all():
            meta.append((query_statements(mode, event.id), event))
    return render_template("speech_update_show.html", mode=mode, meta=meta)


@speech.route("/add", methods=["GET", "POST"])
@user_permission.require()
def add():
    speaker_name = request.args.get("speaker", None)
    add_form = AddStatementForm()
    if add_form.validate_on_submit():
        speaker_name = add_form["speaker_name"].data
        event_id = add_form["event"].data
    if speaker_name is None or event_id is None:
        flash("Missing data", "alert-error")
        return redirect(url_for(".index"))
    speaker = Speaker.query.filter_by(name=speaker_name).filter_by(event=event_id).first()
    if not speaker:
        speaker = Speaker(speaker_name, event_id)
        db.session.add(speaker)
        db.session.commit()
    if Statement.query.filter_by(speaker=speaker.id).filter_by(event=event_id).filter_by(executed=False).count() > 0:
        flash("Speaker already listet", "alert-error")
        return redirect(url_for(request.args.get("next") or ".show"))
    statement = Statement(speaker.id, event_id)
    db.session.add(statement)
    db.session.commit()
    mode = request.args.get("mode", "pending")
    event_id = request.args.get("event", None)
    return redirect(url_for(request.args.get("next") or ".index", mode=mode, event=event_id))


@speech.route("/cancel")
@user_permission.require()
def cancel():
    statement_id = request.args.get("statement", None)
    event_id = request.args.get("event", -1)
    if not statement_id:
        flash("Missing statement id", "alert-error")
        return redirect(url_for(request.args.get("next") or ".index"))
    statement = Statement.query.filter_by(id=statement_id).first()
    db.session.delete(statement)
    db.session.commit()
    flash("Statement canceled", "alert-success")
    mode = request.args.get("mode", "pending")
    return redirect(url_for(request.args.get("next") or ".index", mode=mode, event=event_id))

@speech.route("/done")
@user_permission.require()
def done():
    statement_id = request.args.get("statement", None)
    event_id = request.args.get("event", -1)
    if not statement_id:
        flash("Missing statement id", "alert-error")
        return redirect(url_for(request.args.get("next") or ".index"))
    statement = Statement.query.filter_by(id=statement_id).first()
    if statement.done():
        db.session.commit()
    else:
        flash("Statement already done", "alert-error")
    mode = request.args.get("mode", "pending")
    return redirect(url_for(request.args.get("next") or ".index", mode=mode, event=event_id))

@speech.route("/update_show.js")
def update_show_js():
    mode = request.args.get("mode", "pending")
    event_id = request.args.get("event", -1)
    return render_template("update_show.js", mode=mode, event_id=event_id)

