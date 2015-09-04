from flask.ext.login import UserMixin

from datetime import datetime

from shared import db

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    roles = db.Column(db.PickleType)
    temp_key = db.Column(db.String)
    temp_key_timestamp = db.Column(db.DateTime)
    
    def __init__(self, fullname, username, password, roles=None):
        self.fullname = fullname
        self.username = username
        self.password = password
        self.roles = roles
        self.temp_key = ""
        self.temp_key_timestamp = datetime(1970, 1, 1, 0, 0)
    
    def __repr__(self):
        return "<User(id={}, fullname='{}', username='{}', password'{}', roles{}, temp_key='{}', temp_key_timestamp={})>".format(
            self.id, 
            self.fullname, 
            self.username, 
            self.password, 
            self.roles,
            self.temp_key,
            self.temp_key_timestamp
        )


class Speaker(db.Model):
    __tablename__ = "speakers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return "<Speaker(id={}, name={})>".format(self.id, self.name)


class Statement(db.Model):
    __tablename__ = "statements"
    id = db.Column(db.Integer, primary_key=True)
    speaker = db.Column(db.Integer, db.ForeignKey("speakers.id"), nullable=False)
    insertion_time = db.Column(db.DateTime)
    executed = db.Column(db.Boolean)
    execution_time = db.Column(db.DateTime)
    
    def __init__(self, speaker, insertion_time=None, executed=False, execution_time=None):
        self.speaker = speaker
        self.insertion_time = insertion_time or datetime.now()
        self.executed = executed
        self.execution_time = execution_time or datetime.now()
    
    def __repr__(self):
        return "<Statement(id={}, speaker={}, insertion_time={}, executed={}, execution_time={})>".format(
            self.id, 
            self.speaker,
            self.insertion_time,
            self.executed,
            self.execution_time
        )
    
    def dump(self):
        return { "speaker": self.speaker, "insertion_time": self.insertion_time.timestamp(), "executed": self.executed, "execution_time": self.execution_time.timestamp() }
    
    def done(self):
        if self.executed:
            return False
        self.executed = True
        self.execution_time = datetime.now()
        return True
    
