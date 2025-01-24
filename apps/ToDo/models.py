from datetime import datetime
from pytz import timezone
from app import db


def get_current_time():
    return datetime.now(tz=timezone("Europe/Zurich")).replace(second=0, microsecond=0)


class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True, default=get_current_time)
    user = db.Column(db.Integer)
    task = db.Column(db.Text())
    state = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=get_current_time)
    to_do_date = db.Column(db.DateTime, default=get_current_time)
