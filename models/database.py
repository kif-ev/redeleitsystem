form flask.ext.login import UserMixin

from shared import db

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    roles = db.Column(db.PickleType)
    
    def __init__(self, fullname, username, password, roles=None):
        self.fullname = fullname
        self.username = username
        self.password = password
        self.roles = roles
    
    def __repr__(self):
        return "<User(id={}, fullname='{}', username='{}', password'{}', roles'{})>".format(self.id, self.fullname, self.username, self.password, self.roles)
