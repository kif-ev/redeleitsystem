from flask import abort, render_template
from datetime import datetime

from models.database import Speaker

from shared import db

def render_layout(template, **kwargs):
    current_time = datetime.now()
    return render_template(template, current_time=current_time, **kwargs)
       
def speaker_by_name_or_number(name_or_number, event_id):
    if name_or_number.isnumeric():
        number = int(name_or_number)
        speaker = Speaker.query.filter_by(number=number).first()
        if speaker is not None:
            return speaker
        else:
            speaker = Speaker("", number, event_id)
            db.session.add(speaker)
            db.session.commit()
            return speaker
    else:
        name = name_or_number
        speaker = Speaker.query.filter_by(name=name).first()
        if speaker is not None:
            return speaker
        else:
            speaker = Speaker(name, 0, event_id)
            db.session.add(speaker)
            db.session.commit()
            return speaker
 
