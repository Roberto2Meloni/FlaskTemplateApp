from datetime import datetime
from pytz import timezone
from app import db


def get_current_time():
    return datetime.now(tz=timezone("Europe/Zurich")).replace(second=0, microsecond=0)


class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=get_current_time)
    user = db.Column(db.String(255))
    task = db.Column(db.String(255))
    state = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=get_current_time)
