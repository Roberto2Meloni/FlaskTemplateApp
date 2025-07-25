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


class PrintHubDiscountProfile(db.Model):
    __tablename__ = "printhub_discount_profile"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name des Profils
    discount_type = db.Column(
        db.String(20), nullable=False, default="discount"
    )  # "discount" oder "surcharge"
    percentage = db.Column(
        db.Numeric(5, 2), nullable=False
    )  # 0.00 bis 100.00 (immer positiv)
    notes = db.Column(db.Text, nullable=True)  # Notizen/Beschreibung

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Metadata
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<PrintHubDiscountProfile {self.name} ({self.discount_type}: {self.percentage}%)>"

    @staticmethod
    def get_discount_types():
        """Verfügbare Rabatt/Aufschlag-Typen"""
        return [("discount", "Rabatt"), ("surcharge", "Aufschlag")]

    @staticmethod
    def get_by_user(username, include_inactive=False):
        """Alle Rabatt/Aufschlag-Profile eines Benutzers"""
        query = PrintHubDiscountProfile.query.filter_by(created_by=username)
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(
            PrintHubDiscountProfile.discount_type.asc(),  # Rabatte zuerst
            PrintHubDiscountProfile.percentage.desc(),  # Dann nach Höhe
        ).all()

    @staticmethod
    def search(username, search_term=None, include_inactive=False):
        """Rabatt/Aufschlag-Profile suchen"""
        query = PrintHubDiscountProfile.query.filter_by(created_by=username)

        if not include_inactive:
            query = query.filter_by(is_active=True)

        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    PrintHubDiscountProfile.name.ilike(search_pattern),
                    PrintHubDiscountProfile.notes.ilike(search_pattern),
                )
            )

        return query.order_by(
            PrintHubDiscountProfile.discount_type.asc(),
            PrintHubDiscountProfile.percentage.desc(),
        ).all()

    @property
    def discount_type_display(self):
        """Anzeige-Text für Discount-Typ"""
        type_options = dict(self.get_discount_types())
        return type_options.get(self.discount_type, "Unbekannt")

    @property
    def percentage_display(self):
        """Formatierte Anzeige mit Typ"""
        return f"{float(self.percentage):.1f}% {self.discount_type_display}"

    @property
    def calculation_factor(self):
        """Berechnungsfaktor (z.B. 0.9 für 10% Rabatt, 1.3 für 30% Aufschlag)"""
        if self.discount_type == "discount":
            return 1 - (float(self.percentage) / 100)  # Rabatt = weniger bezahlen
        elif self.discount_type == "surcharge":
            return 1 + (float(self.percentage) / 100)  # Aufschlag = mehr bezahlen
        else:
            return 1.0  # Neutral

    @property
    def signed_percentage(self):
        """Gibt den Prozentsatz mit Vorzeichen zurück (für Berechnungen)"""
        if self.discount_type == "discount":
            return float(self.percentage)  # Positiv für Rabatt
        elif self.discount_type == "surcharge":
            return -float(self.percentage)  # Negativ für Aufschlag
        else:
            return 0.0

    @property
    def is_discount(self):
        """Prüft ob es ein Rabatt ist"""
        return self.discount_type == "discount"

    @property
    def is_surcharge(self):
        """Prüft ob es ein Aufschlag ist"""
        return self.discount_type == "surcharge"

    @property
    def status_color(self):
        """Bootstrap-Farbe für Status-Badge"""
        return "success" if self.is_active else "secondary"

    @property
    def type_badge_class(self):
        """CSS-Klasse basierend auf Typ"""
        if self.is_discount:
            return "badge-success"  # Grün für Rabatte
        elif self.is_surcharge:
            return "badge-warning"  # Orange für Aufschläge
        else:
            return "badge-secondary"  # Grau für neutral

    @property
    def amount_badge_class(self):
        """CSS-Klasse für Betrag-Badge basierend auf Höhe"""
        value = float(self.percentage)
        if value >= 30:
            return "badge-danger"  # Hoher Betrag (rot)
        elif value >= 15:
            return "badge-warning"  # Mittlerer Betrag (orange)
        elif value >= 5:
            return "badge-info"  # Niedriger Betrag (blau)
        else:
            return "badge-light"  # Sehr niedriger Betrag (hell)

    def calculate_adjustment_amount(self, original_price):
        """Berechnet den Anpassungs-Betrag für einen gegebenen Preis"""
        adjustment = float(original_price) * (float(self.percentage) / 100)
        return round(adjustment, 2)

    def calculate_final_price(self, original_price):
        """Berechnet den Endpreis nach Anpassung"""
        final_price = float(original_price) * self.calculation_factor
        return round(final_price, 2)

    def get_pricing_details(self, original_price):
        """Gibt detaillierte Preis-Informationen zurück"""
        adjustment_amount = self.calculate_adjustment_amount(original_price)
        final_price = self.calculate_final_price(original_price)

        return {
            "original_price": round(float(original_price), 2),
            "type": self.discount_type,
            "type_display": self.discount_type_display,
            "percentage": float(self.percentage),
            "adjustment_amount": adjustment_amount,
            "final_price": final_price,
            "is_discount": self.is_discount,
            "is_surcharge": self.is_surcharge,
            "profile_name": self.name,
            "calculation_factor": self.calculation_factor,
        }

    def to_dict(self):
        """Konvertiert zu Dictionary für JSON-API"""
        return {
            "id": self.id,
            "name": self.name,
            "discount_type": self.discount_type,
            "discount_type_display": self.discount_type_display,
            "percentage": float(self.percentage),
            "percentage_display": self.percentage_display,
            "signed_percentage": self.signed_percentage,
            "calculation_factor": self.calculation_factor,
            "is_discount": self.is_discount,
            "is_surcharge": self.is_surcharge,
            "type_badge_class": self.type_badge_class,
            "amount_badge_class": self.amount_badge_class,
            "is_active": self.is_active,
            "status_color": self.status_color,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Zu models.py hinzufügen:


class PrintHubQuote(db.Model):
    __tablename__ = "printhub_quotes"

    id = db.Column(db.Integer, primary_key=True)

    # Auftragsdaten
    order_name = db.Column(db.String(200), nullable=False)
    customer_name = db.Column(db.String(200), nullable=True)

    # Globale Kalkulationsgrundlagen
    global_printer_id = db.Column(db.Integer, nullable=True)
    global_energy_profile_id = db.Column(db.Integer, nullable=True)
    global_work_profile_id = db.Column(db.Integer, nullable=True)
    global_overhead_profile_id = db.Column(db.Integer, nullable=True)
    global_discount_profile_id = db.Column(db.Integer, nullable=True)

    # Berechnete Totals
    total_cost = db.Column(db.Numeric(10, 2), nullable=False)
    total_time = db.Column(db.Numeric(8, 2), nullable=False)  # Druckzeit
    total_work_time = db.Column(db.Numeric(8, 2), nullable=False)  # Arbeitszeit

    # Kostenaufschlüsselung
    total_machine_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_material_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_energy_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_work_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_overhead_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    # Status
    status = db.Column(
        db.String(20), nullable=False, default="draft"
    )  # draft, sent, accepted, rejected
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    # Metadata
    created_by = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=get_current_time)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=get_current_time, onupdate=get_current_time
    )

    # Relationships
    suborders = db.relationship(
        "PrintHubSubOrder", backref="quote", lazy=True, cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<PrintHubQuote {self.order_name} - CHF {self.total_cost}>"

    @property
    def status_color(self):
        """Bootstrap-Farbe für Status"""
        colors = {
            "draft": "secondary",
            "sent": "primary",
            "accepted": "success",
            "rejected": "danger",
        }
        return colors.get(self.status, "secondary")

    @property
    def status_display(self):
        """Deutsche Anzeige für Status"""
        displays = {
            "draft": "Entwurf",
            "sent": "Gesendet",
            "accepted": "Angenommen",
            "rejected": "Abgelehnt",
        }
        return displays.get(self.status, "Unbekannt")

    @staticmethod
    def get_by_user(username, include_archived=False):
        """Alle Quotes eines Benutzers"""
        query = PrintHubQuote.query.filter_by(created_by=username)
        if not include_archived:
            query = query.filter_by(is_archived=False)
        return query.order_by(PrintHubQuote.created_at.desc()).all()

    def to_dict(self):
        """Konvertiert zu Dictionary"""
        return {
            "id": self.id,
            "order_name": self.order_name,
            "customer_name": self.customer_name,
            "total_cost": float(self.total_cost),
            "total_time": float(self.total_time),
            "total_work_time": float(self.total_work_time),
            "status": self.status,
            "status_display": self.status_display,
            "status_color": self.status_color,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "suborders_count": len(self.suborders),
            "cost_breakdown": {
                "machine_cost": float(self.total_machine_cost),
                "material_cost": float(self.total_material_cost),
                "energy_cost": float(self.total_energy_cost),
                "work_cost": float(self.total_work_cost),
                "overhead_cost": float(self.total_overhead_cost),
            },
        }


class PrintHubSubOrder(db.Model):
    __tablename__ = "printhub_suborders"

    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key zur Quote
    quote_id = db.Column(
        db.Integer, db.ForeignKey("printhub_quotes.id"), nullable=False
    )

    # Suborder-Daten
    name = db.Column(db.String(200), nullable=False)
    filament_id = db.Column(db.Integer, nullable=False)  # ID des verwendeten Filaments
    filament_usage_grams = db.Column(db.Integer, nullable=False)

    # Zeiten
    print_time_hours = db.Column(db.Numeric(8, 2), nullable=False)
    work_time_hours = db.Column(db.Numeric(8, 2), nullable=False)  # Neue Arbeitszeit

    # Verwendete Profile (können global oder individuell sein)
    printer_id = db.Column(db.Integer, nullable=True)  # NULL = global verwenden
    energy_profile_id = db.Column(db.Integer, nullable=True)  # NULL = global verwenden
    work_profile_id = db.Column(db.Integer, nullable=True)  # NULL = global verwenden
    overhead_profile_id = db.Column(
        db.Integer, nullable=True
    )  # NULL = global verwenden

    # Berechnete Kosten
    machine_cost = db.Column(db.Numeric(10, 2), nullable=False)
    material_cost = db.Column(db.Numeric(10, 2), nullable=False)
    energy_cost = db.Column(db.Numeric(10, 2), nullable=False)
    work_cost = db.Column(db.Numeric(10, 2), nullable=False)
    overhead_cost = db.Column(db.Numeric(10, 2), nullable=False)
    suborder_total = db.Column(db.Numeric(10, 2), nullable=False)

    # Snapshot-Daten für Historisierung (falls Profile später geändert werden)
    printer_name = db.Column(db.String(100), nullable=True)
    filament_name = db.Column(db.String(200), nullable=True)
    printer_cost_per_hour = db.Column(db.Numeric(8, 4), nullable=True)
    energy_cost_per_kwh = db.Column(db.Numeric(8, 4), nullable=True)
    work_cost_per_hour = db.Column(db.Numeric(8, 2), nullable=True)
    overhead_cost_per_hour = db.Column(db.Numeric(8, 4), nullable=True)

    def __repr__(self):
        return f"<PrintHubSubOrder {self.name} - CHF {self.suborder_total}>"

    def to_dict(self):
        """Konvertiert zu Dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "filament_usage_grams": self.filament_usage_grams,
            "print_time_hours": float(self.print_time_hours),
            "work_time_hours": float(self.work_time_hours),
            "machine_cost": float(self.machine_cost),
            "material_cost": float(self.material_cost),
            "energy_cost": float(self.energy_cost),
            "work_cost": float(self.work_cost),
            "overhead_cost": float(self.overhead_cost),
            "suborder_total": float(self.suborder_total),
            "printer_name": self.printer_name,
            "filament_name": self.filament_name,
        }
