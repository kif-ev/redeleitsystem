from flask.ext.login import UserMixin

from datetime import datetime

from shared import db

from sqlalchemy.orm import relationship, backref

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
        
class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return "<Event(id={}, name={})>".format(self.id, self.name)

class Topic(db.Model):
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    mode = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    event = relationship("Event", backref=backref("topics",order_by=id))
    
    
    def __init__(self, name, mode, event_id):
        self.name = name
        self.mode = mode
        self.event_id = event_id
    
    def __repr__(self):
        return "<Topic(id={}, name='{}', mode='{}', event_id={})>".format(
            self.id, 
            self.name, 
            self.mode,
            self.event_id
        )
    

class Speaker(db.Model):
    __tablename__ = "speakers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    event = relationship("Event", backref=backref("speakers",order_by=id))
    
    def __init__(self, name, event_id):
        self.name = name
        self.event_id = event_id
    
    def __repr__(self):
        return "<Speaker(id={}, name='{}', event_id={})>".format(
            self.id, 
            self.name,
            self.event_id
        )


class Statement(db.Model):
    __tablename__ = "statements"
    id = db.Column(db.Integer, primary_key=True)
    speaker_id = db.Column(db.Integer, db.ForeignKey("speakers.id"), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    insertion_time = db.Column(db.DateTime)
    executed = db.Column(db.Boolean)
    execution_time = db.Column(db.DateTime)

    speaker = relationship("Speaker", backref=backref("statements",order_by=id))
    event = relationship("Event", backref=backref("statements",order_by=id))
    
    def __init__(self, speaker_id, event_id, insertion_time=None, executed=False, execution_time=None):
        self.speaker_id = speaker_id
        self.event_id = event_id
        self.insertion_time = insertion_time or datetime.now()
        self.executed = executed
        self.execution_time = execution_time or datetime.now()
    
    def __repr__(self):
        return "<Statement(id={}, speaker={}, event_id={}, topic_id={}, insertion_time={}, executed={}, execution_time={})>".format(
            self.id, 
            self.speaker,
            self.event_id,
            self.topic_id,
            self.insertion_time,
            self.executed,
            self.execution_time
        )
    
    def done(self):
        if self.executed:
            return False
        self.executed = True
        self.execution_time = datetime.now()
        return True
    
