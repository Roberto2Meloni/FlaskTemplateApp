from datetime import datetime
from pytz import timezone
from app import db


def get_current_time():
    return datetime.now(tz=timezone("Europe/Zurich")).replace(second=0, microsecond=0)


class ToDo_UltimateNote(db.Model):
    __tablename__ = "todo_ultimate_note"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    archived_at = db.Column(db.DateTime, nullable=True)
    archived = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<ToDo_Ultimate {self.text}>"
