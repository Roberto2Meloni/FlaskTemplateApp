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
    electricity_monthly = db.Column(db.Numeric(10, 2), nullable=False, default=0)
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
            + float(self.electricity_monthly)
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
            "electricity_monthly": float(self.electricity_monthly),
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
