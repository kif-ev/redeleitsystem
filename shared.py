from flask import abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.principal import Permission, RoleNeed

db = SQLAlchemy()
login_manager = LoginManager()

admin_permission = Permission(RoleNeed("admin"))
user_permission = Permission(RoleNeed("user"))
roles = ["user", "admin"]
