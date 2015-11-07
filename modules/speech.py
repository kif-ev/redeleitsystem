from flask import Blueprint, redirect, url_for, request, flash, abort, send_file, Response
from flask.ext.login import login_required

from models.database import User, Statement, Speaker, Topic
from models.forms import AddStatementForm

from shared import db, admin_permission, user_permission, render_layout

from datetime import datetime
import json

import config

speech = Blueprint("speech", __name__)

def query_statements(mode, topic_id):
    statements = db.session.query(Statement).filter_by(topic=topic_id).all()
    speakers = db.session.query(Speaker).filter_by(topic=topic_id).all()
    if mode == "balanced" or mode == "pending":
        count = { speaker.id: 0 for speaker in speakers }
        for statement in statements:
            if statement.speaker in count:
                count[statement.speaker] += 1
            else:
                count[statement.speaker] = 1
        sorted_speakers = sorted(speakers, key=lambda sp: count[sp.id])
        result = []
        for speaker in sorted_speakers:
            pending_statements = [statement for statement in statements if statement.speaker == speaker.id and not statement.executed]
            if len(pending_statements) > 0:
                result.append((pending_statements[0], speaker, count[speaker.id]))
        return result
    
    if mode == "fifo":
        speaker_by_id = { speaker.id: speaker for speaker in speakers }
        result = [(statement, speaker_by_id[statement.speaker], 0) for statement in statements if not statement.executed]
        return result
    
    print("unknown querying mode {}".format(mode))

@speech.route("/index")
def index():
    topic_id = request.args.get("topic", None) 
    mode = request.args.get("mode", None)
    meta = []
    if topic_id is not None and topic_id != "-1":
        topic = Topic.query.filter_by(id=topic_id).first()
        form = AddStatementForm()
        form.topic.data = topic.id
        meta.append((query_statements(mode if mode is not None else topic.mode, topic_id), form, topic))
    else:
        for topic in Topic.query.all():
            form = AddStatementForm()
            form.topic.data = topic.id
            meta.append((query_statements(mode if mode is not None else topic.mode, topic.id), form, topic))
        topic_id = -1
    return render_layout("speech_index.html", meta=meta, topic_id=topic_id, mode=mode)

@speech.route("/show")
def show():
    topic_id = request.args.get("topic", None)
    mode = request.args.get("mode", None) 
    meta = []
    if topic_id is not None and topic_id is not "-1":
        topic = Topic.query.filter_by(id=topic_id).first()
        meta.append((query_statements(mode if mode is not None else topic.mode, topic_id), topic))
    else:
        for topic in Topic.query.all():
            meta.append((query_statements(mode if mode is not None else topic.mode, topic.id), topic))
    return render_layout("speech_show.html", mode=mode, meta=meta, topic_id=topic_id)

@speech.route("/update")
def update():
    topic_id = request.args.get("topic", None)
    mode = request.args.get("mode", None) 
    meta = []
    if topic_id is not None and topic_id != "-1":
        topic = Topic.query.filter_by(id=topic_id).first()
        meta.append((query_statements(mode if mode is not None else topic.mode, topic_id), topic))
    else:
        for topic in Topic.query.all():
            meta.append((query_statements(mode if mode is not None else topic.mode, topic.id), topic))
    return render_layout("speech_content_show.html", mode=mode, meta=meta)


@speech.route("/add", methods=["GET", "POST"])
@user_permission.require()
def add():
    speaker_name = request.args.get("speaker", None)
    add_form = AddStatementForm()
    if add_form.validate_on_submit():
        speaker_name = add_form["speaker_name"].data
        topic_id = add_form["topic"].data
    if speaker_name is None or topic_id is None:
        flash("Missing data", "alert-error")
        return redirect(url_for(".index"))
    speaker = Speaker.query.filter_by(name=speaker_name).filter_by(topic=topic_id).first()
    if not speaker:
        speaker = Speaker(speaker_name, topic_id)
        db.session.add(speaker)
        db.session.commit()
    if Statement.query.filter_by(speaker=speaker.id).filter_by(topic=topic_id).filter_by(executed=False).count() > 0:
        flash("Speaker already listet", "alert-error")
        return redirect(url_for(request.args.get("next") or ".show"))
    statement = Statement(speaker.id, topic_id)
    db.session.add(statement)
    db.session.commit()
    mode = request.args.get("mode", None)
    topic_id = request.args.get("topic", None)
    return redirect(url_for(request.args.get("next") or ".index", mode=mode, topic=topic_id))


@speech.route("/cancel")
@user_permission.require()
def cancel():
    statement_id = request.args.get("statement", None)
    topic_id = request.args.get("topic", -1)
    if not statement_id:
        flash("Missing statement id", "alert-error")
        return redirect(url_for(request.args.get("next") or ".index"))
    statement = Statement.query.filter_by(id=statement_id).first()
    db.session.delete(statement)
    db.session.commit()
    flash("Statement canceled", "alert-success")
    mode = request.args.get("mode", None)
    return redirect(url_for(request.args.get("next") or ".index", mode=mode, topic=topic_id))

@speech.route("/done")
@user_permission.require()
def done():
    statement_id = request.args.get("statement", None)
    topic_id = request.args.get("topic", -1)
    if not statement_id:
        flash("Missing statement id", "alert-error")
        return redirect(url_for(request.args.get("next") or ".index"))
    statement = Statement.query.filter_by(id=statement_id).first()
    if statement.done():
        db.session.commit()
    else:
        flash("Statement already done", "alert-error")
    mode = request.args.get("mode", None)
    return redirect(url_for(request.args.get("next") or ".index", mode=mode, topic=topic_id))

@speech.route("/update_show.js")
def update_show_js():
    update_interval = config.UPDATE_SHOW_INTERVAL or 1
    div = "rede-content-div"
    mode = request.args.get("mode", None)
    topic_id = request.args.get("topic", -1)
    target_url = url_for(".update", mode=mode, topic=topic_id)
    return render_layout("update.js", update_interval=update_interval, div=div, target_url=target_url, prefix="update_show_")

