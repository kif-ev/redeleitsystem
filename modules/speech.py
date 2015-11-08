from flask import Blueprint, redirect, url_for, request, flash, abort, send_file, Response
from flask.ext.login import login_required

from models.database import User, Statement, Speaker, Topic, Event
from models.forms import AddStatementForm

from shared import db, admin_permission, user_permission
from utils import render_layout

from datetime import datetime
import json

import config

speech = Blueprint("speech", __name__)


@speech.route("/")
def index():
    event_id = request.args.get("event", None)
    events = []
    if event_id is not None and event_id.isnumeric() and int(event_id) > -1:
        event = Event.query.filter_by(id=event_id).first()
        if event is not None:
            events.append(event)
    else:
        events = Event.query.all()
    return render_layout("speech_index.html", events=events, event=-1 if len(events) != 1 else events[0].id)

@speech.route("/update")
def update():
    event_id = request.args.get("event", None)
    events = []
    if event_id is not None and event_id.isnumeric() and int(event_id) > -1:
        event = Event.query.filter_by(id=event_id).first()
        if event is not None:
            events.append(event)
    else:
        events = Event.query.all()
    return render_layout("speech_content_index.html", events=events)

@speech.route("/update_index.js")
def update_index_js():
    update_interval = config.UPDATE_INDEX_INTERVAL or 1
    div = "rede-content-div"
    mode = request.args.get("mode", None)
    event_id = request.args.get("event", -1)
    target_url = url_for(".update", event=event_id)
    return render_layout("update.js", update_interval=update_interval, div=div, target_url=target_url, prefix="update_index_")

