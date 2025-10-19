from datetime import datetime
from pytz import timezone
from app import db


def get_current_time():
    return datetime.now(tz=timezone("Europe/Zurich")).replace(second=0, microsecond=0)


class NexusPlayerFiles(db.Model):
    __tablename__ = "NexusPlayerFiles"
    id = db.Column(db.Integer, primary_key=True)
    file_uuid = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)  # User ID, ohne FK
    last_modified_by = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "file_uuid": self.file_uuid,
            "name": self.name,
            "path": self.path,
            "type": self.type,
            "size": self.size,
            "last_modified": self.last_modified,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "last_modified_by": self.last_modified_by,
        }


class NexusPlayerPlaylists(db.Model):
    __tablename__ = "NexusPlayerPlaylists"
    id = db.Column(db.Integer, primary_key=True)
    playlist_uuid = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, nullable=False)  # User ID, ohne FK
    last_modified = db.Column(db.DateTime, nullable=False)
    last_modified_by = db.Column(db.String(255), nullable=False)
    count_elements = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "playlist_uuid": self.playlist_uuid,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "last_modified": self.last_modified,
            "last_modified_by": self.last_modified_by,
            "count_elements": self.count_elements,
        }
