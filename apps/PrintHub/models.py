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


class PrintHubPrinter(db.Model):
    __tablename__ = "printhub_printers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name des Druckers
    brand = db.Column(db.String(50), nullable=False)  # Marke (Prusa, Creality, etc.)
    machine_cost_per_hour = db.Column(
        db.Numeric(6, 2), nullable=False
    )  # Maschinenkosten pro Stunde in CHF
    energy_consumption = db.Column(
        db.Integer, nullable=True
    )  # Energieverbrauch in Watt (optional)
    notes = db.Column(db.Text, nullable=True)  # Optionale Notizen

    # Zeitstempel
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False
    )

    # Benutzer als Username String
    created_by = db.Column(
        db.String(64), nullable=False
    )  # Speichert current_user.username

    def __repr__(self):
        return f"<PrintHubPrinter {self.name} ({self.brand})>"

    @property
    def daily_machine_cost(self):
        """Berechnet die täglichen Maschinenkosten bei 24h Betrieb"""
        return float(self.machine_cost_per_hour) * 24

    def estimate_print_cost(self, print_time_hours, filament_cost=0):
        """Schätzt die Druckkosten basierend auf Zeit und Filament"""
        machine_cost = float(self.machine_cost_per_hour) * print_time_hours

        # Energiekosten berechnen (falls verfügbar)
        energy_cost = 0
        if self.energy_consumption:
            # Annahme: 0.25 CHF pro kWh
            energy_kwh = (self.energy_consumption / 1000) * print_time_hours
            energy_cost = energy_kwh * 0.25

        total_cost = machine_cost + energy_cost + filament_cost

        return {
            "machine_cost": round(machine_cost, 2),
            "energy_cost": round(energy_cost, 2),
            "filament_cost": round(filament_cost, 2),
            "total_cost": round(total_cost, 2),
        }

    def to_dict(self):
        """Konvertiert das Model zu einem Dictionary für JSON-Responses"""
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "machine_cost_per_hour": float(self.machine_cost_per_hour),
            "energy_consumption": self.energy_consumption,
            "daily_machine_cost": self.daily_machine_cost,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }

    @staticmethod
    def get_common_brands():
        """Gibt häufige Drucker-Marken zurück"""
        return [
            "Prusa",
            "Creality",
            "Bambu Lab",
            "Ultimaker",
            "Formlabs",
            "Artillery",
            "Anycubic",
            "Elegoo",
            "QIDI",
            "Voron",
            "Andere",
        ]

    @classmethod
    def get_by_user(cls, username):
        """Holt alle Drucker eines bestimmten Benutzers"""
        return (
            cls.query.filter_by(created_by=username)
            .order_by(cls.created_at.desc())
            .all()
        )

    @classmethod
    def search(cls, username, search_term=None):
        """Sucht Drucker mit optionalen Filtern"""
        query = cls.query.filter_by(created_by=username)

        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    cls.name.ilike(search),
                    cls.brand.ilike(search),
                    cls.notes.ilike(search),
                )
            )

        return query.order_by(cls.created_at.desc()).all()
