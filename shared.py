from flask import abort, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.principal import Permission, RoleNeed
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()

admin_permission = Permission(RoleNeed("admin"))
user_permission = Permission(RoleNeed("user"))
roles = ["user", "admin"]

def render_layout(template, **kwargs):
    current_time = datetime.now()
    return render_template(template, current_time=current_time, **kwargs)
