from datetime import datetime
from pytz import timezone
from app import db


def get_current_time():
    return datetime.now(tz=timezone("Europe/Zurich")).replace(second=0, microsecond=0)


class DoMemoryIcon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    technic_type = db.Column(db.String(255), nullable=False)  # Block, Schlag, Dachi
    technic_korp = db.Column(db.String(255))  # Arm, Bein
    icon = db.Column(db.String(255), nullable=False)
    technic_level = db.Column(db.String(255), nullable=False)
    technic_name = db.Column(db.String(255), nullable=False)
