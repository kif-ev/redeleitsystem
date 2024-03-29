from flask.ext.login import UserMixin

from datetime import datetime
import random

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
        return "<User(id={}, fullname='{}', username='{}', password='{}', roles={}, temp_key='{}', temp_key_timestamp={})>".format(
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
    paused = db.Column(db.Boolean)
    paused_until = db.Column(db.DateTime)
    current_topic_id = db.Column(db.Integer)
    
    topics = relationship("Topic", backref=backref("event"), cascade="all, delete-orphan")
    speakers = relationship("Speaker", backref=backref("event"), cascade="all, delete-orphan")
    
    def __init__(self, name, paused=False, current_topic_id=None):
        self.name = name
        self.paused = paused
        self.paused_until = datetime(1970, 1, 1)
        self.current_topic_id = current_topic_id or -1
    
    def __repr__(self):
        return "<Event(id={}, name={}, paused={}, paused_until={})>".format(
            self.id, 
            self.name, 
            self.paused,
            self.paused_until
        )
    
    def sorted_topics(self):
        return sorted(self.topics, key=lambda tp: tp.get_index())
    
    def get_current_topic(self):
        candidates = [topic for topic in self.topics if topic.id == self.current_topic_id]
        if len(candidates) < 1:
            return None
        return candidates[0]

class Topic(db.Model):
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    mode = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))
    index = db.Column(db.Integer)

    statements = relationship("Statement", backref=backref("topic"), cascade="all, delete-orphan")
    
    def __init__(self, name, mode, event_id):
        self.name = name
        self.mode = mode
        self.event_id = event_id
        self.index = None
    
    def __repr__(self):
        return "<Topic(id={}, name='{}', mode='{}', event_id={}, index={})>".format(
            self.id, 
            self.name, 
            self.mode,
            self.event_id,
            self.index
        )
    
    def sorted_statements(self):
        statements = [statement for statement in self.statements if not statement.executed]
        if self.mode == "fifo":
            return sorted(statements, key=lambda st:-2 if st.is_current else -1 if st.is_meta else st.id)
        elif self.mode == "balanced":
            return sorted(statements, key=lambda st:(-2,st.id) if st.is_current else (-1,st.id) if st.is_meta else (st.speaker.count(self), st.id))
        elif self.mode == "random":
            return sorted(statements, key=lambda st:random.random())
        else:
            return statements
    
    def swap_topics(self, other):
        other.index, self.index = self.get_index(), other.get_index()

    def get_index(self):
        if self.index == None:
            return self.id
        return self.index
    
    def get_next_index(self):
        topics = self.event.sorted_topics()
        i = topics.index(self) + 1
        if i >= len(topics):
            i = -1
        return topics[i].id
    
    def get_previous_index(self):
        topics = self.event.sorted_topics()
        i = topics.index(self) - 1
        if i >= len(topics):
            i = 0
        return topics[i].id

class Speaker(db.Model):
    __tablename__ = "speakers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    number = db.Column(db.Integer)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"))

    statements = relationship("Statement", backref=backref("speaker"), cascade="all, delete-orphan")
    
    def __init__(self, name, number, event_id):
        self.name = name
        self.number = number
        self.event_id = event_id
    
    def __repr__(self):
        return "<Speaker(id={}, number={}, name='{}', event_id={})>".format(
            self.id, 
            self.number,
            self.name,
            self.event_id
        )
    
    def identifier(self):
        if self.number == 0:
            return self.name
        elif self.name == "":
            return self.number
        else:
            return "{} ({})".format(self.name, self.number)
    
    def count(self, topic):
        return len([statement for statement in self.statements if statement.topic == topic and not statement.is_meta])
    
    def count_active(self, topic):
        return len([statement for statement in self.statements if statement.topic == topic and not statement.executed and not statement.is_meta])
        
    def count_active_meta(self, topic):
        return len([statement for statement in self.statements if statement.topic == topic and not statement.executed and statement.is_meta])
        

class Statement(db.Model):
    __tablename__ = "statements"
    id = db.Column(db.Integer, primary_key=True)
    speaker_id = db.Column(db.Integer, db.ForeignKey("speakers.id"))
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
    insertion_time = db.Column(db.DateTime)
    executed = db.Column(db.Boolean)
    execution_time = db.Column(db.DateTime)
    is_meta = db.Column(db.Boolean, default=False)
    is_current = db.Column(db.Boolean, default=False)

    
    def __init__(self, speaker_id, topic_id, insertion_time=None, executed=False, execution_time=None, is_meta=False, is_current=False):
        self.speaker_id = speaker_id
        self.topic_id = topic_id
        self.insertion_time = insertion_time or datetime.now()
        self.executed = executed
        self.execution_time = execution_time or datetime.now()
        self.is_meta = is_meta
        self.is_current = is_current
    
    def __repr__(self):
        return "<Statement(id={}, speaker={}, topic_id={}, insertion_time={}, executed={}, execution_time={}, is_meta={}, is_current={})>".format(
            self.id, 
            self.speaker,
            self.topic_id,
            self.insertion_time,
            self.executed,
            self.execution_time,
            self.is_meta,
            self.is_current
        )
    
    def done(self):
        if self.executed:
            return False
        self.executed = True
        self.is_current = False
        self.execution_time = datetime.now()
        if self.topic.sorted_statements() is not None and self.topic.sorted_statements():
            self.topic.sorted_statements()[0].is_current = True
        return True
    
    def undo(self):
        if not self.executed:
            return False
        self.topic.sorted_statements()[0].is_current = False
        self.executed = False
        self.is_current = True
        
