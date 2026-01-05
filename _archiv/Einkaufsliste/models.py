from app import db, login
from datetime import datetime
from pytz import timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event
import jwt
from time import time
from app import app
from hashlib import md5


def get_current_time():
    return datetime.now(tz=timezone("Europe/Zurich")).replace(second=0, microsecond=0)


# Hilfstabelle für viele-zu-viele Beziehung zwischen Group und User
group_membership = db.Table(
    "group_membership",
    db.Column(
        "group_id",
        db.Integer,
        db.ForeignKey("einkaufsliste_group.group_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),  # users statt user!
        primary_key=True,
    ),
)


class EinkaufslisteGroup(db.Model):
    __tablename__ = "einkaufsliste_group"
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(250), unique=True)
    created_date = db.Column(db.DateTime, index=True, default=get_current_time)
    group_owner = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="SET NULL")
    )  # users statt user!

    # Verwende explizite primaryjoin für die owner-Relationship
    owner = db.relationship(
        "User",
        primaryjoin="EinkaufslisteGroup.group_owner == User.id",
        foreign_keys=[group_owner],
    )
    group_members = db.relationship(
        "User",
        secondary=group_membership,
        primaryjoin="EinkaufslisteGroup.group_id == group_membership.c.group_id",
        secondaryjoin="User.id == group_membership.c.user_id",
        backref=db.backref(
            "einkaufsliste_groups", lazy="dynamic"
        ),  # Eindeutiger backref-Name
        lazy="dynamic",
    )
    group_public = db.Column(db.Boolean, default=False)
    group_visible = db.Column(db.Boolean, default=True)


class EinkaufslisteList(db.Model):
    __tablename__ = "einkaufsliste_list"
    list_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # users statt user!
    group_id = db.Column(db.Integer, db.ForeignKey("einkaufsliste_group.group_id"))

    # Relationships mit korrekten String-Referenzen
    user = db.relationship("User", backref="lists")
    group = db.relationship("EinkaufslisteGroup", backref="lists")
    items = db.relationship(
        "EinkaufslisteItem", backref="list", cascade="all, delete-orphan"
    )
    others = db.relationship(
        "EinkaufslisteOther", backref="list", cascade="all, delete-orphan"
    )

    created_date = db.Column(db.DateTime, index=True, default=get_current_time)
    first_day = db.Column(db.DateTime)
    last_day = db.Column(db.DateTime)

    @staticmethod
    def parse_date(date_str):
        try:
            return datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Must be in dd.mm.yyyy format.")

    @property
    def first_day_str(self):
        return self.first_day.strftime("%d.%m.%Y") if self.first_day else ""

    @first_day_str.setter
    def first_day_str(self, date_str):
        self.first_day = self.parse_date(date_str) if date_str else None

    @property
    def last_day_str(self):
        return self.last_day.strftime("%d.%m.%Y") if self.last_day else ""

    @last_day_str.setter
    def last_day_str(self, date_str):
        self.last_day = self.parse_date(date_str) if date_str else None


class EinkaufslisteItem(db.Model):
    __tablename__ = "einkaufsliste_item"
    item_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # users statt user!
    list_id = db.Column(db.Integer, db.ForeignKey("einkaufsliste_list.list_id"))
    item_name = db.Column(db.String(150))
    created_date = db.Column(db.DateTime, index=True, default=get_current_time)
    to_eat_day = db.Column(db.DateTime)
    meal = db.Column(db.String(150))
    buy = db.Column(db.Boolean, default=False)

    # Relationship zum User
    user = db.relationship("User", backref="items")


class EinkaufslisteOther(db.Model):
    __tablename__ = "einkaufsliste_other"
    other_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))  # users statt user!
    list_id = db.Column(db.Integer, db.ForeignKey("einkaufsliste_list.list_id"))
    other_name = db.Column(db.String(250))
    created_date = db.Column(db.DateTime, index=True, default=get_current_time)
    buy = db.Column(db.Boolean, default=False)

    # Relationship zum User
    user = db.relationship("User", backref="others")
