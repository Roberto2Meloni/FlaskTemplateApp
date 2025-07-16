from app import db
from datetime import datetime
from sqlalchemy import func
from pytz import timezone


# Globale Funktion für Zeitstempel
def get_current_time():
    """Gibt die aktuelle Zeit in Schweizer Zeitzone zurück"""
    return datetime.now(tz=timezone("Europe/Zurich")).replace(second=0, microsecond=0)


class PrintHubFilament(db.Model):
    __tablename__ = "printhub_filaments"

    id = db.Column(db.Integer, primary_key=True)
    filament_type = db.Column(
        db.String(20), nullable=False, index=True
    )  # PLA, PETG, TPU, etc.
    name = db.Column(db.String(100), nullable=False)  # Bezeichnung
    manufacturer = db.Column(db.String(50), nullable=False)  # Hersteller
    weight = db.Column(db.Integer, nullable=False)  # Gewicht in Gramm
    price = db.Column(db.Numeric(8, 2), nullable=False)  # Preis in CHF
    notes = db.Column(db.Text, nullable=True)  # Optionale Notizen

    # EINFACHE LÖSUNG: Verwende UTC und konvertiere später
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Benutzer als Username String (nicht ID)
    created_by = db.Column(
        db.String(64), nullable=False
    )  # Speichert current_user.username

    def __repr__(self):
        return f"<PrintHubFilament {self.name} ({self.filament_type})>"

    @property
    def created_at_swiss(self):
        """Gibt created_at in Schweizer Zeit zurück"""
        if self.created_at:
            # Konvertiere UTC zu Schweizer Zeit
            utc_time = self.created_at.replace(tzinfo=timezone("UTC"))
            swiss_time = utc_time.astimezone(timezone("Europe/Zurich"))
            return swiss_time.replace(second=0, microsecond=0)
        return None

    @property
    def updated_at_swiss(self):
        """Gibt updated_at in Schweizer Zeit zurück"""
        if self.updated_at:
            # Konvertiere UTC zu Schweizer Zeit
            utc_time = self.updated_at.replace(tzinfo=timezone("UTC"))
            swiss_time = utc_time.astimezone(timezone("Europe/Zurich"))
            return swiss_time.replace(second=0, microsecond=0)
        return None

    @property
    def price_per_kg(self):
        """Berechnet den Preis pro Kilogramm"""
        if self.weight > 0:
            return round(float(self.price) / self.weight * 1000, 2)
        return 0.0

    @property
    def type_badge_class(self):
        """Gibt die CSS-Klasse für das Typ-Badge zurück"""
        type_classes = {
            "PLA": "badge-pla",
            "PETG": "badge-petg",
            "TPU": "badge-tpu",
            "ABS": "badge-abs",
            "WOOD": "badge-wood",
            "CARBON": "badge-carbon",
        }
        return type_classes.get(self.filament_type, "badge-secondary")

    def to_dict(self):
        """Konvertiert das Model zu einem Dictionary für JSON-Responses"""
        return {
            "id": self.id,
            "filament_type": self.filament_type,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "weight": self.weight,
            "price": float(self.price),
            "price_per_kg": self.price_per_kg,
            "notes": self.notes,
            "created_at": (
                self.created_at_swiss.isoformat() if self.created_at_swiss else None
            ),
            "updated_at": (
                self.updated_at_swiss.isoformat() if self.updated_at_swiss else None
            ),
            "type_badge_class": self.type_badge_class,
            "created_by": self.created_by,
        }

    @staticmethod
    def get_filament_types():
        """Gibt alle verfügbaren Filament-Typen zurück"""
        return ["PLA", "PETG", "TPU", "ABS", "WOOD", "CARBON"]

    @classmethod
    def get_by_user(cls, username):
        """Holt alle Filamente eines bestimmten Benutzers"""
        return (
            cls.query.filter_by(created_by=username)
            .order_by(cls.created_at.desc())
            .all()
        )

    @classmethod
    def search(cls, username, search_term=None, filament_type=None):
        """Sucht Filamente mit optionalen Filtern"""
        query = cls.query.filter_by(created_by=username)

        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    cls.name.ilike(search),
                    cls.manufacturer.ilike(search),
                    cls.notes.ilike(search),
                )
            )

        if filament_type:
            query = query.filter_by(filament_type=filament_type)

        return query.order_by(cls.created_at.desc()).all()
