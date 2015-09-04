from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, send_file, Response
from flask.ext.login import login_required

from models.database import User, Statement, Speaker
from models.forms import AddStatementForm

from shared import db, admin_permission, user_permission

from datetime import datetime
import json

speech = Blueprint("speech", __name__)

def transpose(arr):
    print(list)
    return list(map(list, zip(*arr)))

def query_statements(mode):
    statements = []
    if mode == "pending":
        statements = db.session.query(Statement, Speaker, db.func.count(Statement.speaker).label("total")).group_by(Speaker.id).join(Speaker).order_by("total ASC", Statement.insertion_time).all()
    elif mode == "all":
        statements = db.session.query(Statement, Speaker).join(Speaker).order_by(Statement.insertion_time).all()
    elif mode == "past":
        statements = db.session.query(Statement, Speaker).join(Speaker).filter(Statement.executed == True).order_by(Statement.execution_time).all()
    return statements

@speech.route("/index")
def index():
    mode = request.args.get("mode", "pending")
    statements = query_statements(mode)
    add_form = AddStatementForm()
    current = ".index"
    return render_template("speech_index.html", statements=statements, add_form=add_form, current=current)

@speech.route("/show")
def show():
    mode = request.args.get("mode", "pending") 
    statements = query_statements(mode)
    current = ".show"
    return render_template("speech_show.html", statements=statements, current=current, mode=mode)

@speech.route("/update")
def update():
    mode = request.args.get("mode", "pending")
    statements = query_statements(mode)
    return render_template("speech_update_show.html", statements=statements, mode=mode)


@speech.route("/add", methods=["GET", "POST"])
@user_permission.require()
def add():
    speaker_name = request.args.get("speaker", None)
    add_form = AddStatementForm()
    if add_form.validate_on_submit():
        speaker_name = add_form["speaker_name"].data
    if speaker_name is None:
        flash("Missing speaker name", "alert-error")
        return redirect(url_for(".show"))
    speaker = Speaker.query.filter_by(name=speaker_name).first()
    if not speaker:
        speaker = Speaker(speaker_name)
        db.session.add(speaker)
        db.session.commit()
    if Statement.query.filter_by(speaker=speaker.id).filter_by(executed=False).count() > 0:
        flash("Speaker already listet", "alert-error")
        return redirect(url_for(request.args.get("next") or ".show"))
    statement = Statement(speaker.id)
    db.session.add(statement)
    db.session.commit()
    mode = request.args.get("mode", "pending")
    return redirect(url_for(request.args.get("next") or ".index", mode=mode))


@speech.route("/cancel")
@user_permission.require()
def cancel():
    statement_id = request.args.get("statement", None)
    if not statement_id:
        flash("Missing statement id", "alert-error")
        return redirect(url_for(request.args.get("next") or ".index"))
    statement = Statement.query.filter_by(id=statement_id).first()
    db.session.delete(statement)
    db.session.commit()
    flash("Statement canceled", "alert-success")
    mode = request.args.get("mode", "pending")
    return redirect(url_for(request.args.get("next") or ".index", mode=mode))

@speech.route("/done")
@user_permission.require()
def done():
    statement_id = request.args.get("statement", None)
    if not statement_id:
        flash("Missing statement id", "alert-error")
        return redirect(url_for(request.args.get("next") or ".index"))
    statement = Statement.query.filter_by(id=statement_id).first()
    if statement.done():
        db.session.commit()
    else:
        flash("Statement already done", "alert-error")
    mode = request.args.get("mode", "pending")
    return redirect(url_for(request.args.get("next") or ".index", mode=mode))

@speech.route("/update_show.js")
def update_show_js():
    mode = request.args.get("mode", "pending")
    return render_template("update_show.js", mode=mode)

