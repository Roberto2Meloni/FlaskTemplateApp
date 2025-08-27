from datetime import datetime
from pytz import timezone
from app import db


def get_current_time():
    return datetime.now(tz=timezone("Europe/Zurich")).replace(second=0, microsecond=0)


class CalculatorCalcWay(db.Model):
    __tablename__ = "CalculatorCalcWay"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    calc_way = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)

    def __repr__(self):
        return f"<CalculatorCalcWay {self.calc_way}>"
