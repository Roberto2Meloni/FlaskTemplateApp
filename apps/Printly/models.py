from datetime import datetime
from pytz import timezone
from app import db


def get_current_time():
    return datetime.now(tz=timezone("Europe/Zurich")).replace(second=0, microsecond=0)


class PrintlyPrinter(db.Model):
    __tablename__ = "printly_printers"

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

    # Friedhof Atribute
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<PrintlyPrinter {self.name} ({self.brand})>"

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


class PrintlyFilament(db.Model):
    __tablename__ = "printly_filaments"

    id = db.Column(db.Integer, primary_key=True)
    filament_type = db.Column(
        db.String(20), nullable=False, index=True
    )  # PLA, PETG, TPU, etc.
    name = db.Column(db.String(100), nullable=False)  # z.B. "PLA Volcanic Black"
    color = db.Column(
        db.String(50), nullable=True
    )  # optional, via GUI aus Name extrahiert
    manufacturer = db.Column(db.String(50), nullable=False)  # Filamentum, Prusa, etc.
    diameter = db.Column(
        db.Numeric(3, 2), nullable=False, default=1.75
    )  # 1.75 oder 2.85 mm
    weight = db.Column(
        db.Integer, nullable=False
    )  # Gewicht in Gramm (750, 1000, 2300...)
    price = db.Column(db.Numeric(8, 2), nullable=False)  # Preis in CHF
    notes = db.Column(db.Text, nullable=True)  # Optionale Notizen
    is_archived = db.Column(db.Boolean, default=False, nullable=False)  # Friedhof

    # Zeitstempel
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False
    )

    # Benutzer
    created_by = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return (
            f"<PrintlyFilament {self.name} ({self.filament_type}, {self.diameter}mm)>"
        )

    # ----------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------

    @property
    def price_per_gram(self):
        """Preis pro Gramm – für Offertenkalkulation"""
        if self.weight > 0:
            return round(float(self.price) / self.weight, 4)
        return 0.0

    @property
    def price_per_kg(self):
        """Preis pro Kilogramm"""
        if self.weight > 0:
            return round(float(self.price) / self.weight * 1000, 2)
        return 0.0

    @property
    def type_badge_class(self):
        """CSS-Klasse für Typ-Badge"""
        type_classes = {
            "PLA": "badge-pla",
            "PETG": "badge-petg",
            "TPU": "badge-tpu",
            "ABS": "badge-abs",
            "ASA": "badge-asa",
            "WOOD": "badge-wood",
            "CARBON": "badge-carbon",
            "NYLON": "badge-nylon",
        }
        return type_classes.get(self.filament_type, "badge-secondary")

    # ----------------------------------------------------------
    # SERIALISIERUNG
    # ----------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "filament_type": self.filament_type,
            "name": self.name,
            "color": self.color,
            "manufacturer": self.manufacturer,
            "diameter": float(self.diameter),
            "weight": self.weight,
            "price": float(self.price),
            "price_per_gram": self.price_per_gram,
            "price_per_kg": self.price_per_kg,
            "notes": self.notes,
            "is_archived": self.is_archived,
            "type_badge_class": self.type_badge_class,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }

    # ----------------------------------------------------------
    # STATISCHE HILFSMETHODEN
    # ----------------------------------------------------------

    @staticmethod
    def get_filament_types():
        return ["PLA", "PETG", "TPU", "ABS", "ASA", "WOOD", "CARBON", "NYLON", "Andere"]

    @staticmethod
    def get_manufacturers():
        return [
            "Filamentum",
            "Prusa",
            "Bambu Lab",
            "Polymaker",
            "eSUN",
            "Prusament",
            "Andere",
        ]

    @staticmethod
    def get_diameters():
        return [1.75, 2.85]
