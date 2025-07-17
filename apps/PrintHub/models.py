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


# Model für Energiekosten (PrintHubEnergyCost)
class PrintHubEnergyCost(db.Model):
    __tablename__ = "printhub_energy_cost"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # z.B. "Grundtarif 2024"
    provider = db.Column(db.String(100), nullable=False)  # z.B. "EWZ", "Axpo"
    cost_per_kwh = db.Column(db.Numeric(10, 4), nullable=False)  # CHF pro kWh
    base_fee_monthly = db.Column(
        db.Numeric(10, 2), nullable=True
    )  # Monatliche Grundgebühr
    tariff_type = db.Column(
        db.String(50), nullable=True
    )  # "Einfach", "Tag/Nacht", "Smart"
    valid_from = db.Column(db.Date, nullable=True)
    valid_until = db.Column(db.Date, nullable=True)
    night_rate = db.Column(
        db.Numeric(10, 4), nullable=True
    )  # Nachttarif falls verfügbar
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Metadata
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def get_tariff_types():
        return [
            "Einfachtarif",
            "Doppeltarif (Tag/Nacht)",
            "Smart Tarif",
            "Gewerbe",
            "Industrie",
        ]

    @staticmethod
    def get_by_user(username, include_inactive=False):
        query = PrintHubEnergyCost.query.filter_by(created_by=username)
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(PrintHubEnergyCost.cost_per_kwh.asc()).all()

    @staticmethod
    def search(username, search_term=None, provider=None, include_inactive=False):
        query = PrintHubEnergyCost.query.filter_by(created_by=username)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    PrintHubEnergyCost.name.ilike(search_pattern),
                    PrintHubEnergyCost.provider.ilike(search_pattern),
                    PrintHubEnergyCost.notes.ilike(search_pattern),
                )
            )

        if provider:
            query = query.filter(PrintHubEnergyCost.provider.ilike(f"%{provider}%"))

        return query.order_by(PrintHubEnergyCost.cost_per_kwh.asc()).all()

    @property
    def annual_base_fee(self):
        return float(self.base_fee_monthly or 0) * 12

    @property
    def cost_per_kwh_display(self):
        return f"CHF {float(self.cost_per_kwh):.4f}"

    @property
    def is_current(self):
        today = datetime.now().date()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return True

    @property
    def status_color(self):
        if not self.is_active:
            return "secondary"
        elif not self.is_current:
            return "warning"
        else:
            return "success"


# Zu Ihrer models.py hinzufügen:


class PrintHubWorkHours(db.Model):
    __tablename__ = "printhub_work_hours"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name des Mitarbeiters
    role = db.Column(db.String(50), nullable=False)  # Rolle/Position
    cost_per_hour = db.Column(
        db.Numeric(8, 2), nullable=False
    )  # Kosten pro Stunde in CHF

    # Metadata
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<PrintHubWorkHours {self.name} ({self.role})>"

    @staticmethod
    def get_roles():
        """Verfügbare Rollen/Positionen"""
        return [
            "3D-Designer",
            "CAD-Spezialist",
            "Techniker",
            "Qualitätskontrolle",
            "Post-Processing",
            "Projektmanager",
            "Allrounder",
            "Praktikant",
            "Freelancer",
        ]

    @staticmethod
    def get_by_user(username):
        """Alle Arbeitszeiten eines Benutzers"""
        return (
            PrintHubWorkHours.query.filter_by(created_by=username)
            .order_by(PrintHubWorkHours.cost_per_hour.desc())
            .all()
        )

    @staticmethod
    def search(username, search_term=None, role=None):
        """Arbeitszeiten suchen"""
        query = PrintHubWorkHours.query.filter_by(created_by=username)

        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    PrintHubWorkHours.name.ilike(search_pattern),
                    PrintHubWorkHours.role.ilike(search_pattern),
                )
            )

        if role:
            query = query.filter(PrintHubWorkHours.role.ilike(f"%{role}%"))

        return query.order_by(PrintHubWorkHours.cost_per_hour.desc()).all()

    @property
    def cost_per_hour_display(self):
        """Formatierte Anzeige der Kosten pro Stunde"""
        return f"CHF {float(self.cost_per_hour):.2f}"

    @property
    def daily_cost(self):
        """Tageskosten bei 8h Arbeitszeit"""
        return float(self.cost_per_hour) * 8

    @property
    def monthly_cost(self):
        """Monatliche Kosten bei 160h (20 Arbeitstage × 8h)"""
        return float(self.cost_per_hour) * 160

    def estimate_project_cost(self, hours_needed):
        """Schätzt Projektkosten basierend auf benötigten Stunden"""
        cost = float(self.cost_per_hour) * hours_needed
        return {
            "hours": hours_needed,
            "hourly_rate": float(self.cost_per_hour),
            "total_cost": round(cost, 2),
        }

    def to_dict(self):
        """Konvertiert zu Dictionary für JSON-API"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "cost_per_hour": float(self.cost_per_hour),
            "cost_per_hour_display": self.cost_per_hour_display,
            "daily_cost": self.daily_cost,
            "monthly_cost": self.monthly_cost,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Zu Ihrer models.py hinzufügen:


class PrintHubOverheadProfile(db.Model):
    __tablename__ = "printhub_overhead_profile"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name des Profils
    location = db.Column(db.String(200), nullable=True)  # Standort/Beschreibung

    # Fixkosten pro Monat (alle in CHF)
    rent_monthly = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # Miete
    heating_electricity = db.Column(
        db.Numeric(10, 2), nullable=False, default=0
    )  # Heizung/Strom
    insurance = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # Versicherung
    internet = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # Internet

    # Software-Lizenzen
    software_cost = db.Column(
        db.Numeric(10, 2), nullable=False, default=0
    )  # Software-Kosten
    software_billing = db.Column(
        db.String(20), nullable=False, default="monthly"
    )  # "monthly" oder "yearly"

    other_costs = db.Column(
        db.Numeric(10, 2), nullable=False, default=0
    )  # Weitere Kosten

    # Produktionsplanung
    planned_hours_monthly = db.Column(
        db.Integer, nullable=False, default=100
    )  # Geplante Stunden/Monat

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Metadata
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<PrintHubOverheadProfile {self.name}>"

    @staticmethod
    def get_software_billing_options():
        """Verfügbare Abrechnungsarten für Software"""
        return [("monthly", "Monatlich"), ("yearly", "Jährlich")]

    @staticmethod
    def get_by_user(username, include_inactive=False):
        """Alle Overhead-Profile eines Benutzers"""
        query = PrintHubOverheadProfile.query.filter_by(created_by=username)
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(PrintHubOverheadProfile.name.asc()).all()

    @staticmethod
    def search(username, search_term=None, include_inactive=False):
        """Overhead-Profile suchen"""
        query = PrintHubOverheadProfile.query.filter_by(created_by=username)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    PrintHubOverheadProfile.name.ilike(search_pattern),
                    PrintHubOverheadProfile.location.ilike(search_pattern),
                    PrintHubOverheadProfile.notes.ilike(search_pattern),
                )
            )

        return query.order_by(PrintHubOverheadProfile.name.asc()).all()

    @property
    def software_cost_monthly(self):
        """Gibt Software-Kosten pro Monat zurück (konvertiert von yearly falls nötig)"""
        if self.software_billing == "yearly":
            return float(self.software_cost) / 12
        return float(self.software_cost)

    @property
    def total_monthly_costs(self):
        """Gesamte monatliche Fixkosten"""
        return (
            float(self.rent_monthly)
            + float(self.heating_electricity)
            + float(self.insurance)
            + float(self.internet)
            + self.software_cost_monthly
            + float(self.other_costs)
        )

    @property
    def overhead_per_hour(self):
        """Overhead-Kosten pro Stunde"""
        if self.planned_hours_monthly > 0:
            return self.total_monthly_costs / self.planned_hours_monthly
        return 0.0

    @property
    def status_color(self):
        """Bootstrap-Farbe für Status-Badge"""
        return "success" if self.is_active else "secondary"

    @property
    def software_billing_display(self):
        """Anzeige-Text für Software-Abrechnung"""
        billing_options = dict(self.get_software_billing_options())
        return billing_options.get(self.software_billing, "Unbekannt")

    def calculate_overhead_for_hours(self, hours):
        """Berechnet Overhead-Kosten für gegebene Stunden"""
        return round(self.overhead_per_hour * hours, 2)

    def to_dict(self):
        """Konvertiert zu Dictionary für JSON-API"""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "rent_monthly": float(self.rent_monthly),
            "heating_electricity": float(self.heating_electricity),
            "insurance": float(self.insurance),
            "internet": float(self.internet),
            "software_cost": float(self.software_cost),
            "software_billing": self.software_billing,
            "software_billing_display": self.software_billing_display,
            "software_cost_monthly": self.software_cost_monthly,
            "other_costs": float(self.other_costs),
            "planned_hours_monthly": self.planned_hours_monthly,
            "total_monthly_costs": self.total_monthly_costs,
            "overhead_per_hour": round(self.overhead_per_hour, 4),
            "is_active": self.is_active,
            "status_color": self.status_color,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
