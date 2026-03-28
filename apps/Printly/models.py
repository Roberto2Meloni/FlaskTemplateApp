from datetime import datetime
from pytz import timezone
from app import db


def get_current_time():
    return datetime.now(tz=timezone("Europe/Zurich")).replace(second=0, microsecond=0)


def generate_company_number():
    """Generiert automatische Firmennummer F-XXXX"""
    last = PrintlyCompany.query.order_by(PrintlyCompany.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    return f"F-{next_id:04d}"


def generate_customer_number():
    """Generiert automatische Kundennummer K-XXXX"""
    last = PrintlyCustomer.query.order_by(PrintlyCustomer.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    return f"K-{next_id:04d}"


def generate_quote_number():
    last = PrintlyQuote.query.order_by(PrintlyQuote.id.desc()).first()
    next_id = (last.id + 1) if last else 1
    return f"Q-{next_id:04d}"


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

    @property
    def overhead_profiles_with_default(self):
        """Gibt Overhead-Profile mit is_default Flag zurück"""
        from .models import printly_printer_overhead

        results = []
        for profile in self.overhead_profiles.all():
            row = db.session.execute(
                db.select(printly_printer_overhead).where(
                    printly_printer_overhead.c.printer_id == self.id,
                    printly_printer_overhead.c.overhead_id == profile.id,
                )
            ).fetchone()
            results.append(
                {
                    "profile": profile,
                    "is_default": row.is_default if row else False,
                }
            )
        return results

    @property
    def total_cost_per_hour(self):
        """Maschinenkosten + Standard-Overhead"""
        machine = float(self.machine_cost_per_hour)
        # Standard-Overhead finden
        default_overhead = next(
            (
                p["profile"]
                for p in self.overhead_profiles_with_default
                if p["is_default"]
            ),
            None,
        )
        overhead = float(default_overhead.overhead_per_hour) if default_overhead else 0
        return round(machine + overhead, 4)

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


class PrintlyElectricityCost(db.Model):
    __tablename__ = "printly_electricity_costs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # z.B. "Grundtarif 2024"
    provider = db.Column(db.String(100), nullable=False)  # z.B. "EWZ", "Axpo"
    cost_per_kwh = db.Column(db.Numeric(10, 4), nullable=False)  # CHF pro kWh
    base_fee_monthly = db.Column(
        db.Numeric(10, 2), nullable=True
    )  # Monatliche Grundgebühr
    tariff_type = db.Column(db.String(50), nullable=True)  # "Einfachtarif", etc.
    valid_from = db.Column(db.Date, nullable=True)
    valid_until = db.Column(db.Date, nullable=True)
    night_rate = db.Column(
        db.Numeric(10, 4), nullable=True
    )  # Nachttarif falls verfügbar
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Zeitstempel
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False
    )
    created_by = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"<PrintlyEnergyCost {self.name} ({self.provider})>"

    # ----------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------

    @property
    def annual_base_fee(self):
        """Jährliche Grundgebühr"""
        return round(float(self.base_fee_monthly or 0) * 12, 2)

    @property
    def is_current(self):
        """Tarif aktuell gültig basierend auf Datum"""
        today = datetime.now(tz=timezone("Europe/Zurich")).date()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_until and today > self.valid_until:
            return False
        return True

    @property
    def status(self):
        """Status-String für Anzeige"""
        if not self.is_active:
            return "inactive"
        elif not self.is_current:
            return "expired"
        else:
            return "active"

    # ----------------------------------------------------------
    # SERIALISIERUNG
    # ----------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "cost_per_kwh": float(self.cost_per_kwh),
            "base_fee_monthly": (
                float(self.base_fee_monthly) if self.base_fee_monthly else None
            ),
            "annual_base_fee": self.annual_base_fee,
            "tariff_type": self.tariff_type,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "night_rate": float(self.night_rate) if self.night_rate else None,
            "is_active": self.is_active,
            "is_current": self.is_current,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }

    # ----------------------------------------------------------
    # STATISCHE HILFSMETHODEN
    # ----------------------------------------------------------

    @staticmethod
    def get_tariff_types():
        return [
            "Einfachtarif",
            "Doppeltarif (Tag/Nacht)",
            "Smart Tarif",
            "Gewerbe",
            "Industrie",
            "Andere",
        ]


class PrintlyWorkHours(db.Model):
    __tablename__ = "printly_work_hours"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # z.B. "Normaler Stundensatz"
    cost_per_hour = db.Column(db.Numeric(8, 2), nullable=False)  # CHF/h
    notes = db.Column(db.Text, nullable=True)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    # Zeitstempel
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False
    )
    created_by = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"<PrintlyWorkHours {self.name} ({self.cost_per_hour} CHF/h)>"

    # ----------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------

    @property
    def daily_cost(self):
        """Tageskosten bei 8h"""
        return round(float(self.cost_per_hour) * 8, 2)

    @property
    def monthly_cost(self):
        """Monatliche Kosten bei 160h (20 Tage × 8h)"""
        return round(float(self.cost_per_hour) * 160, 2)

    # ----------------------------------------------------------
    # SERIALISIERUNG
    # ----------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "cost_per_hour": float(self.cost_per_hour),
            "daily_cost": self.daily_cost,
            "monthly_cost": self.monthly_cost,
            "notes": self.notes,
            "is_archived": self.is_archived,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }


# ============================================================
# MANY-TO-MANY VERKNÜPFUNGSTABELLE
# ============================================================

printly_printer_overhead = db.Table(
    "printly_printer_overhead",
    db.Column(
        "printer_id", db.Integer, db.ForeignKey("printly_printers.id"), nullable=False
    ),
    db.Column(
        "overhead_id",
        db.Integer,
        db.ForeignKey("printly_overhead_profiles.id"),
        nullable=False,
    ),
    db.Column("is_default", db.Boolean, default=False, nullable=False),
    db.PrimaryKeyConstraint("printer_id", "overhead_id"),
)


# ============================================================
# OVERHEAD PROFIL
# ============================================================


class PrintlyOverheadProfile(db.Model):
    __tablename__ = "printly_overhead_profiles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # z.B. "Zuhause", "Hobbyraum"
    location = db.Column(db.String(200), nullable=True)  # Beschreibung des Standorts

    # Fixkosten pro Monat (CHF)
    rent_monthly = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    # electricity_monthly = db.Column(db.Numeric(10, 2), nullable=False, default=0) --> wird nicht benötig, da diese im Stromtarif enthalten sind
    insurance = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    internet = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    other_costs = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    # Software-Lizenzen
    software_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    software_billing = db.Column(
        db.String(20), nullable=False, default="monthly"
    )  # "monthly" / "yearly"

    # Produktionsplanung
    planned_hours_monthly = db.Column(db.Integer, nullable=False, default=100)

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Zeitstempel
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False
    )
    created_by = db.Column(db.String(64), nullable=False)

    # Relationship zu Druckern (via Verknüpfungstabelle)
    printers = db.relationship(
        "PrintlyPrinter",
        secondary=printly_printer_overhead,
        backref=db.backref("overhead_profiles", lazy="dynamic"),
        lazy="dynamic",
    )

    def __repr__(self):
        return f"<PrintlyOverheadProfile {self.name}>"

    # ----------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------

    @property
    def software_cost_monthly(self):
        """Software-Kosten normalisiert auf Monat"""
        if self.software_billing == "yearly":
            return round(float(self.software_cost) / 12, 2)
        return round(float(self.software_cost), 2)

    @property
    def total_monthly_costs(self):
        """Gesamte monatliche Fixkosten"""
        return round(
            float(self.rent_monthly)
            + float(self.insurance)
            + float(self.internet)
            + float(self.other_costs)
            + self.software_cost_monthly,
            2,
        )

    @property
    def overhead_per_hour(self):
        """Overhead-Kosten pro Stunde"""
        if self.planned_hours_monthly > 0:
            return round(self.total_monthly_costs / self.planned_hours_monthly, 4)
        return 0.0

    @property
    def linked_printers(self):
        """Gibt verknüpfte Drucker mit is_default zurück"""
        from sqlalchemy import select

        results = []
        for printer in self.printers:
            # is_default aus Verknüpfungstabelle lesen
            row = db.session.execute(
                db.select(printly_printer_overhead).where(
                    printly_printer_overhead.c.printer_id == printer.id,
                    printly_printer_overhead.c.overhead_id == self.id,
                )
            ).fetchone()
            results.append(
                {
                    "printer": printer,
                    "is_default": row.is_default if row else False,
                }
            )
        return results

    # ----------------------------------------------------------
    # SERIALISIERUNG
    # ----------------------------------------------------------

    def to_dict(self, include_printers=False):
        data = {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "rent_monthly": float(self.rent_monthly),
            "insurance": float(self.insurance),
            "internet": float(self.internet),
            "software_cost": float(self.software_cost),
            "software_billing": self.software_billing,
            "software_cost_monthly": self.software_cost_monthly,
            "other_costs": float(self.other_costs),
            "planned_hours_monthly": self.planned_hours_monthly,
            "total_monthly_costs": self.total_monthly_costs,
            "overhead_per_hour": self.overhead_per_hour,
            "is_active": self.is_active,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
        if include_printers:
            data["printers"] = [
                {
                    "id": p["printer"].id,
                    "name": p["printer"].name,
                    "brand": p["printer"].brand,
                    "is_default": p["is_default"],
                }
                for p in self.linked_printers
            ]
        return data

    # ----------------------------------------------------------
    # STATISCHE HILFSMETHODEN
    # ----------------------------------------------------------

    @staticmethod
    def get_software_billing_options():
        return [("monthly", "Monatlich"), ("yearly", "Jährlich")]


class PrintlyDiscountProfile(db.Model):
    __tablename__ = "printly_discount_profiles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    discount_type = db.Column(
        db.String(20), nullable=False, default="discount"
    )  # "discount" / "surcharge"
    percentage = db.Column(db.Numeric(5, 2), nullable=False)  # 0.00 – 100.00
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Zeitstempel
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False
    )
    created_by = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"<PrintlyDiscountProfile {self.name} ({self.discount_type}: {self.percentage}%)>"

    # ----------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------

    @property
    def is_discount(self):
        return self.discount_type == "discount"

    @property
    def is_surcharge(self):
        return self.discount_type == "surcharge"

    @property
    def calculation_factor(self):
        """Berechnungsfaktor für Offertenkalkulation"""
        if self.is_discount:
            return round(1 - (float(self.percentage) / 100), 6)
        elif self.is_surcharge:
            return round(1 + (float(self.percentage) / 100), 6)
        return 1.0

    def calculate_final_price(self, original_price):
        """Endpreis nach Anpassung"""
        return round(float(original_price) * self.calculation_factor, 2)

    # ----------------------------------------------------------
    # SERIALISIERUNG
    # ----------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "discount_type": self.discount_type,
            "percentage": float(self.percentage),
            "calculation_factor": self.calculation_factor,
            "is_discount": self.is_discount,
            "is_surcharge": self.is_surcharge,
            "is_active": self.is_active,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }

    # ----------------------------------------------------------
    # STATISCHE HILFSMETHODEN
    # ----------------------------------------------------------

    @staticmethod
    def get_discount_types():
        return [("discount", "Rabatt"), ("surcharge", "Aufschlag")]


# ============================================================
# FIRMA
# ============================================================


class PrintlyCompany(db.Model):
    __tablename__ = "printly_companies"

    id = db.Column(db.Integer, primary_key=True)
    company_number = db.Column(db.String(20), unique=True, nullable=False)
    company_name = db.Column(db.String(150), nullable=False)

    # Kontakt
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    website = db.Column(db.String(200), nullable=True)

    # Adresse
    address = db.Column(db.String(200), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(50), nullable=False, default="CH")

    # Standard Rabatt
    # Falls der Rabat gelöscht wird, dann wird die Verknüpfung gelscht
    discount_profile_id = db.Column(
        db.Integer,
        db.ForeignKey("printly_discount_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    discount_profile = db.relationship("PrintlyDiscountProfile", backref="companies")

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Zeitstempel
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False
    )
    created_by = db.Column(db.String(64), nullable=False)

    # Kontaktpersonen
    contacts = db.relationship(
        "PrintlyCustomer",
        backref="company",
        lazy="dynamic",
        foreign_keys="PrintlyCustomer.company_id",
    )

    def __repr__(self):
        return f"<PrintlyCompany {self.company_number} {self.company_name}>"

    @property
    def primary_contact(self):
        return self.contacts.filter_by(is_primary=True).first()

    @property
    def full_address(self):
        parts = []
        if self.address:
            parts.append(self.address)
        if self.zip_code or self.city:
            parts.append(f"{self.zip_code or ''} {self.city or ''}".strip())
        if self.country and self.country != "CH":
            parts.append(self.country)
        return ", ".join(parts) if parts else None

    def to_dict(self, include_contacts=False):
        data = {
            "id": self.id,
            "company_number": self.company_number,
            "company_name": self.company_name,
            "email": self.email,
            "phone": self.phone,
            "website": self.website,
            "address": self.address,
            "zip_code": self.zip_code,
            "city": self.city,
            "country": self.country,
            "full_address": self.full_address,
            "discount_profile_id": self.discount_profile_id,
            "discount_profile": (
                self.discount_profile.name if self.discount_profile else None
            ),
            "is_active": self.is_active,
            "notes": self.notes,
            "contact_count": self.contacts.count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
        if include_contacts:
            data["contacts"] = [c.to_dict() for c in self.contacts.all()]
        return data


# ============================================================
# KUNDE / KONTAKTPERSON
# ============================================================


class PrintlyCustomer(db.Model):
    __tablename__ = "printly_customers"

    id = db.Column(db.Integer, primary_key=True)
    customer_number = db.Column(db.String(20), unique=True, nullable=False)

    # Verknüpfung zur Firma (optional – bei Privatkunden leer)
    company_id = db.Column(
        db.Integer, db.ForeignKey("printly_companies.id"), nullable=True
    )

    # Person
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)

    # Rolle in der Firma
    role = db.Column(db.String(100), nullable=True)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)

    # Kontakt
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(50), nullable=True)

    # Adresse (nur bei Privatkunden relevant)
    address = db.Column(db.String(200), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(50), nullable=False, default="CH")

    # Rabatt (überschreibt Firmenrabatt falls gesetzt)
    # Falls der Rabat gelöscht wird, dann wird die Verknüpfung gelscht
    discount_profile_id = db.Column(
        db.Integer,
        db.ForeignKey("printly_discount_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    discount_profile = db.relationship("PrintlyDiscountProfile", backref="customers")

    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Zeitstempel
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False
    )
    created_by = db.Column(db.String(64), nullable=False)

    def __repr__(self):
        return f"<PrintlyCustomer {self.customer_number} {self.full_name}>"

    # ----------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_company_contact(self):
        return self.company_id is not None

    @property
    def is_private(self):
        return self.company_id is None

    @property
    def effective_discount(self):
        """Eigener Rabatt hat Vorrang, sonst Firmenrabatt"""
        if self.discount_profile:
            return self.discount_profile
        if self.company and self.company.discount_profile:
            return self.company.discount_profile
        return None

    @property
    def full_address(self):
        parts = []
        if self.address:
            parts.append(self.address)
        if self.zip_code or self.city:
            parts.append(f"{self.zip_code or ''} {self.city or ''}".strip())
        if self.country and self.country != "CH":
            parts.append(self.country)
        return ", ".join(parts) if parts else None

    # ----------------------------------------------------------
    # SERIALISIERUNG
    # ----------------------------------------------------------

    def to_dict(self):
        return {
            "id": self.id,
            "customer_number": self.customer_number,
            "company_id": self.company_id,
            "company_name": self.company.company_name if self.company else None,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "role": self.role,
            "is_primary": self.is_primary,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "zip_code": self.zip_code,
            "city": self.city,
            "country": self.country,
            "full_address": self.full_address,
            "discount_profile_id": self.discount_profile_id,
            "discount_profile": (
                self.discount_profile.name if self.discount_profile else None
            ),
            "effective_discount": (
                self.effective_discount.name if self.effective_discount else None
            ),
            "is_company_contact": self.is_company_contact,
            "is_private": self.is_private,
            "is_active": self.is_active,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }


# ============================================================
# OFFERTE
# ============================================================


class PrintlyQuote(db.Model):
    __tablename__ = "printly_quotes"

    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(20), unique=True, nullable=False)

    # Kunde / Firma
    customer_id = db.Column(
        db.Integer, db.ForeignKey("printly_customers.id"), nullable=True
    )
    company_id = db.Column(
        db.Integer, db.ForeignKey("printly_companies.id"), nullable=True
    )
    customer = db.relationship("PrintlyCustomer", backref="quotes")
    company = db.relationship("PrintlyCompany", backref="quotes")

    # Titel / Beschreibung
    title = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)

    # Globale Profile (werden auf alle Suborders angewendet wenn nicht überschrieben)
    global_printer_id = db.Column(
        db.Integer, db.ForeignKey("printly_printers.id"), nullable=True
    )
    global_work_hours_id = db.Column(
        db.Integer, db.ForeignKey("printly_work_hours.id"), nullable=True
    )
    global_overhead_profile_id = db.Column(
        db.Integer, db.ForeignKey("printly_overhead_profiles.id"), nullable=True
    )

    global_printer = db.relationship("PrintlyPrinter", backref="quotes")
    global_work_hours = db.relationship("PrintlyWorkHours", backref="quotes")
    global_overhead_profile = db.relationship(
        "PrintlyOverheadProfile", backref="quotes"
    )

    # Marge (global, überschreibbar pro Suborder)
    margin_percentage = db.Column(db.Numeric(5, 2), nullable=False, default=30)

    # Rabatt (wird auf Endpreis nach Marge angewendet)
    discount_profile_id = db.Column(
        db.Integer, db.ForeignKey("printly_discount_profiles.id"), nullable=True
    )
    discount_profile = db.relationship("PrintlyDiscountProfile", backref="quotes")

    # Berechnete Totals (werden bei jedem Speichern aktualisiert)
    total_self_cost = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_selling_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    # Status
    status = db.Column(db.String(20), nullable=False, default="draft")
    # draft → sent → accepted / rejected → invoiced

    valid_until = db.Column(db.Date, nullable=True)

    # Zeitstempel
    created_at = db.Column(db.DateTime, default=get_current_time, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=get_current_time, onupdate=get_current_time, nullable=False
    )
    created_by = db.Column(db.String(64), nullable=False)

    # Relationen
    suborders = db.relationship(
        "PrintlySubOrder", backref="quote", lazy="dynamic", cascade="all, delete-orphan"
    )
    extra_materials = db.relationship(
        "PrintlyQuoteExtraMaterial",
        backref="quote",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    # ----------------------------------------------------------
    # PROPERTIES
    # ----------------------------------------------------------

    @property
    def status_display(self):
        return {
            "draft": "Entwurf",
            "sent": "Gesendet",
            "accepted": "Angenommen",
            "rejected": "Abgelehnt",
            "invoiced": "Verrechnet",
        }.get(self.status, "Unbekannt")

    @property
    def customer_display(self):
        if self.customer:
            return self.customer.full_name
        if self.company:
            return self.company.company_name
        return "Kein Kunde"

    @property
    def effective_discount_factor(self):
        """Rabattfaktor: 1.0 = kein Rabatt, 0.9 = 10% Rabatt"""
        # Eigener Rabatt auf Offerte hat Vorrang
        if self.discount_profile:
            return float(self.discount_profile.calculation_factor)
        # Sonst Kundenrabatt
        if self.customer and self.customer.effective_discount:
            return float(self.customer.effective_discount.calculation_factor)
        if self.company and self.company.discount_profile:
            return float(self.company.discount_profile.calculation_factor)
        return 1.0

    def recalculate(self):
        """Berechnet alle Totals neu"""
        from decimal import Decimal

        # Aktiven Stromtarif holen
        from app.imported_apps.develop_release.Printly.models import (
            PrintlyElectricityCost,
        )

        energy_tariff = PrintlyElectricityCost.query.filter_by(
            is_active=True, is_current=True
        ).first()
        kwh_rate = float(energy_tariff.cost_per_kwh) if energy_tariff else 0

        total_self = 0.0

        for sub in self.suborders.all():
            sub.calculate(kwh_rate, self)
            total_self += float(sub.self_cost)

        # Zusatzmaterialien
        for mat in self.extra_materials.all():
            total_self += float(mat.total_price)

        # Marge anwenden
        margin = float(self.margin_percentage) / 100
        selling = total_self * (1 + margin)

        # Rabatt anwenden
        selling = selling * self.effective_discount_factor

        self.total_self_cost = round(total_self, 2)
        self.total_selling_price = round(selling, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "quote_number": self.quote_number,
            "title": self.title,
            "customer_display": self.customer_display,
            "customer_id": self.customer_id,
            "company_id": self.company_id,
            "global_printer_id": self.global_printer_id,  # ← NEU
            "global_work_hours_id": self.global_work_hours_id,  # ← NEU
            "global_overhead_profile_id": self.global_overhead_profile_id,  # ← NEU
            "margin_percentage": float(self.margin_percentage),
            "discount_profile_id": self.discount_profile_id,
            "discount_profile": (
                self.discount_profile.name if self.discount_profile else None
            ),
            "effective_discount_factor": self.effective_discount_factor,
            "total_self_cost": float(self.total_self_cost),
            "total_selling_price": float(self.total_selling_price),
            "status": self.status,
            "status_display": self.status_display,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "notes": self.notes,
            "suborders_count": self.suborders.count(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
        }


# ============================================================
# SUBORDER (Druckbett)
# ============================================================


class PrintlySubOrder(db.Model):
    __tablename__ = "printly_suborders"

    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey("printly_quotes.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=1)

    # Druckparameter
    filament_id = db.Column(
        db.Integer, db.ForeignKey("printly_filaments.id"), nullable=True
    )
    filament_usage_grams = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    print_time_hours = db.Column(db.Numeric(8, 4), nullable=False, default=0)
    work_time_hours = db.Column(db.Numeric(8, 4), nullable=False, default=0)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Individuelle Profile (NULL = globales Profil der Offerte verwenden)
    printer_id = db.Column(
        db.Integer, db.ForeignKey("printly_printers.id"), nullable=True
    )
    work_hours_id = db.Column(
        db.Integer, db.ForeignKey("printly_work_hours.id"), nullable=True
    )
    overhead_profile_id = db.Column(
        db.Integer, db.ForeignKey("printly_overhead_profiles.id"), nullable=True
    )

    # Individuelle Marge (NULL = globale Marge der Offerte)
    margin_percentage = db.Column(db.Numeric(5, 2), nullable=True)

    # Relationen
    filament = db.relationship("PrintlyFilament", backref="suborders")
    printer = db.relationship("PrintlyPrinter", backref="suborders")
    work_hours = db.relationship("PrintlyWorkHours", backref="suborders")
    overhead_profile = db.relationship("PrintlyOverheadProfile", backref="suborders")

    # Berechnete Kosten (Snapshot)
    machine_cost = db.Column(db.Numeric(10, 4), nullable=False, default=0)
    material_cost = db.Column(db.Numeric(10, 4), nullable=False, default=0)
    energy_cost = db.Column(db.Numeric(10, 4), nullable=False, default=0)
    work_cost = db.Column(db.Numeric(10, 4), nullable=False, default=0)
    overhead_cost = db.Column(db.Numeric(10, 4), nullable=False, default=0)
    self_cost = db.Column(db.Numeric(10, 4), nullable=False, default=0)

    # Snapshot-Felder (für Historisierung)
    snapshot_printer_name = db.Column(db.String(100), nullable=True)
    snapshot_filament_name = db.Column(db.String(200), nullable=True)
    snapshot_printer_cost_per_hour = db.Column(db.Numeric(8, 4), nullable=True)
    snapshot_filament_price_per_gram = db.Column(db.Numeric(8, 4), nullable=True)
    snapshot_energy_kwh_rate = db.Column(db.Numeric(8, 4), nullable=True)
    snapshot_work_cost_per_hour = db.Column(db.Numeric(8, 2), nullable=True)
    snapshot_overhead_per_hour = db.Column(db.Numeric(8, 4), nullable=True)

    # ----------------------------------------------------------
    # EFFEKTIVE PROFILE (global oder individuell)
    # ----------------------------------------------------------

    def effective_printer(self, quote):
        return self.printer or quote.global_printer

    def effective_work_hours(self, quote):
        return self.work_hours or quote.global_work_hours

    def effective_overhead(self, quote):
        if self.overhead_profile:
            return self.overhead_profile
        if quote.global_overhead_profile:
            return quote.global_overhead_profile
        # Fallback: Standard-Overhead des Druckers
        printer = self.effective_printer(quote)
        if printer:
            default_oh = next(
                (x for x in printer.overhead_profiles_with_default if x["is_default"]),
                None,
            )
            return default_oh["profile"] if default_oh else None
        return None

    def effective_margin(self, quote):
        if self.margin_percentage is not None:
            return float(self.margin_percentage)
        return float(quote.margin_percentage)

    # ----------------------------------------------------------
    # KALKULATION
    # ----------------------------------------------------------

    def calculate(self, kwh_rate, quote):
        printer = self.effective_printer(quote)
        work_hours = self.effective_work_hours(quote)
        overhead = self.effective_overhead(quote)

        h = float(self.print_time_hours)
        w = float(self.work_time_hours)
        g = float(self.filament_usage_grams)

        # Maschinenkosten
        machine_rate = float(printer.machine_cost_per_hour) if printer else 0
        self.machine_cost = round(machine_rate * h, 4)

        # Materialkosten
        filament_rate = float(self.filament.price_per_gram) if self.filament else 0
        self.material_cost = round(filament_rate * g, 4)

        # Energiekosten
        energy_w = (
            float(printer.energy_consumption)
            if printer and printer.energy_consumption
            else 0
        )
        self.energy_cost = round((energy_w / 1000) * h * kwh_rate, 4)

        # Arbeitskosten
        work_rate = float(work_hours.cost_per_hour) if work_hours else 0
        self.work_cost = round(work_rate * w, 4)

        # Overheadkosten
        overhead_rate = float(overhead.overhead_per_hour) if overhead else 0
        self.overhead_cost = round(overhead_rate * h, 4)

        # Selbstkosten total × Anzahl
        subtotal = (
            self.machine_cost
            + self.material_cost
            + self.energy_cost
            + self.work_cost
            + self.overhead_cost
        )
        self.self_cost = round(float(subtotal) * int(self.quantity), 4)

        # Snapshots
        self.snapshot_printer_name = printer.name if printer else None
        self.snapshot_filament_name = self.filament.name if self.filament else None
        self.snapshot_printer_cost_per_hour = machine_rate
        self.snapshot_filament_price_per_gram = filament_rate
        self.snapshot_energy_kwh_rate = kwh_rate
        self.snapshot_work_cost_per_hour = work_rate
        self.snapshot_overhead_per_hour = overhead_rate

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "filament_id": self.filament_id,
            "filament_name": self.filament.name if self.filament else None,
            "filament_usage_grams": float(self.filament_usage_grams),
            "print_time_hours": float(self.print_time_hours),
            "work_time_hours": float(self.work_time_hours),
            "quantity": self.quantity,
            "printer_id": self.printer_id,
            "work_hours_id": self.work_hours_id,
            "overhead_profile_id": self.overhead_profile_id,
            "margin_percentage": (
                float(self.margin_percentage) if self.margin_percentage else None
            ),
            "machine_cost": float(self.machine_cost),
            "material_cost": float(self.material_cost),
            "energy_cost": float(self.energy_cost),
            "work_cost": float(self.work_cost),
            "overhead_cost": float(self.overhead_cost),
            "self_cost": float(self.self_cost),
        }


# ============================================================
# ZUSATZMATERIALIEN
# ============================================================


class PrintlyQuoteExtraMaterial(db.Model):
    __tablename__ = "printly_quote_extra_materials"

    id = db.Column(db.Integer, primary_key=True)
    quote_id = db.Column(db.Integer, db.ForeignKey("printly_quotes.id"), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    notes = db.Column(db.String(200), nullable=True)

    def calculate(self):
        self.total_price = round(float(self.unit_price) * int(self.quantity), 2)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "total_price": float(self.total_price),
            "notes": self.notes,
        }
