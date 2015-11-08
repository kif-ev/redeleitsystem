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
    name = db.Column(db.String, unique=True)
    mode = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    index = db.Column(db.Integer)
    
    event = relationship("Event", backref=backref("topics",order_by=id), foreign_keys=[event_id])
    
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
            return sorted(statements, key=lambda st: -1 if st.is_meta else st.id)
        elif self.mode == "balanced":
            return sorted(statements, key=lambda st: -1 if st.is_meta else st.speaker.count(self))
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
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    event = relationship("Event", backref=backref("speakers",order_by=id))
    
    def __init__(self, name, number, event_id):
        self.name = name
        self.number = number
        self.event_id = event_id
    
    def __repr__(self):
        return "<Speaker(id={}, name='{}', event_id={})>".format(
            self.id, 
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
    speaker_id = db.Column(db.Integer, db.ForeignKey("speakers.id"), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)
    insertion_time = db.Column(db.DateTime)
    executed = db.Column(db.Boolean)
    execution_time = db.Column(db.DateTime)
    is_meta = db.Column(db.Boolean, default=False)

    speaker = relationship("Speaker", backref=backref("statements",order_by=id))
    topic = relationship("Topic", backref=backref("statements",order_by=id))
    
    def __init__(self, speaker_id, topic_id, insertion_time=None, executed=False, execution_time=None, is_meta=False):
        self.speaker_id = speaker_id
        self.topic_id = topic_id
        self.insertion_time = insertion_time or datetime.now()
        self.executed = executed
        self.execution_time = execution_time or datetime.now()
        self.is_meta = is_meta
    
    def __repr__(self):
        return "<Statement(id={}, speaker={}, topic_id={}, insertion_time={}, executed={}, execution_time={}, is_meta={})>".format(
            self.id, 
            self.speaker,
            self.topic_id,
            self.insertion_time,
            self.executed,
            self.execution_time,
            self.is_meta
        )
    
    def done(self):
        if self.executed:
            return False
        self.executed = True
        self.execution_time = datetime.now()
        return True
    
    def undo(self):
        if not self.executed:
            return False
        self.executed = False
        self.execution_time = datetime(1970, 1, 1)
