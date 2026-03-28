"""
Zentrale Seitenkonfiguration für Printly
Neue Seite hinzufügen = nur hier eintragen!
"""

from ..models import (
    PrintlyPrinter,
    PrintlyFilament,
    PrintlyElectricityCost,
    PrintlyWorkHours,
    PrintlyOverheadProfile,
    PrintlyDiscountProfile,
    PrintlyCompany,
    PrintlyCustomer,
)

# ============================================================
# CONTEXT LOADER FUNKTIONEN
# ============================================================


def load_dashboard_context():
    from ..models import (
        PrintlyPrinter,
        PrintlyFilament,
        PrintlyElectricityCost,
        PrintlyWorkHours,
        PrintlyOverheadProfile,
        PrintlyDiscountProfile,
    )

    # Drucker
    active_printers = PrintlyPrinter.query.filter_by(is_archived=False).all()
    graveyard_printers = PrintlyPrinter.query.filter_by(is_archived=True).all()

    # Filamente
    active_filaments = PrintlyFilament.query.filter_by(is_archived=False).all()

    # Stromtarife
    active_energy_costs = PrintlyElectricityCost.query.filter_by(is_active=True).all()
    current_energy = next((e for e in active_energy_costs if e.is_current), None)

    # Arbeitszeiten
    active_work_hours = PrintlyWorkHours.query.filter_by(is_archived=False).all()

    # Overhead Profile
    active_overhead = PrintlyOverheadProfile.query.filter_by(is_active=True).all()

    # Rabatte & Aufschläge
    active_discounts = PrintlyDiscountProfile.query.filter_by(
        is_active=True, discount_type="discount"
    ).all()
    active_surcharges = PrintlyDiscountProfile.query.filter_by(
        is_active=True, discount_type="surcharge"
    ).all()

    # Warnungen berechnen
    warnings = []
    if not active_printers:
        warnings.append(
            {
                "type": "error",
                "icon": "bi-printer",
                "message": "Keine aktiven Drucker erfasst",
            }
        )
    if not active_filaments:
        warnings.append(
            {"type": "error", "icon": "bi-disc", "message": "Keine Filamente erfasst"}
        )
    if not active_energy_costs:
        warnings.append(
            {
                "type": "warning",
                "icon": "bi-lightning-charge",
                "message": "Kein Stromtarif erfasst",
            }
        )
    elif not current_energy:
        warnings.append(
            {
                "type": "warning",
                "icon": "bi-lightning-charge",
                "message": "Kein aktuell gültiger Stromtarif",
            }
        )
    if not active_work_hours:
        warnings.append(
            {
                "type": "warning",
                "icon": "bi-clock",
                "message": "Kein Stundensatz erfasst",
            }
        )
    if not active_overhead:
        warnings.append(
            {
                "type": "warning",
                "icon": "bi-gear",
                "message": "Kein Overhead-Profil erfasst",
            }
        )

    # Drucker ohne Overhead
    printers_without_overhead = [
        p for p in active_printers if p.overhead_profiles.count() == 0
    ]
    if printers_without_overhead:
        warnings.append(
            {
                "type": "info",
                "icon": "bi-link",
                "message": f"{len(printers_without_overhead)} Drucker ohne Overhead-Profil verknüpft",
            }
        )

    # Ø CHF/h Maschinenksosten
    avg_machine_cost = (
        sum(float(p.machine_cost_per_hour) for p in active_printers)
        / len(active_printers)
        if active_printers
        else 0
    )

    # Ø CHF/kg Filament
    avg_filament_price_per_kg = (
        sum(f.price_per_kg for f in active_filaments) / len(active_filaments)
        if active_filaments
        else 0
    )

    return {
        "active_printers": active_printers,
        "graveyard_printers": graveyard_printers,
        "active_filaments": active_filaments,
        "active_energy_costs": active_energy_costs,
        "current_energy": current_energy,
        "active_work_hours": active_work_hours,
        "active_overhead": active_overhead,
        "active_discounts": active_discounts,
        "active_surcharges": active_surcharges,
        "warnings": warnings,
        "avg_machine_cost": round(avg_machine_cost, 2),
        "avg_filament_price_per_kg": round(avg_filament_price_per_kg, 2),
    }


def load_test_context():
    return {}


def load_quote_calculator_context():
    from ..models import (
        PrintlyQuote,
        PrintlyCustomer,
        PrintlyCompany,
        PrintlyPrinter,
        PrintlyWorkHours,
        PrintlyOverheadProfile,
        PrintlyFilament,
        PrintlyDiscountProfile,
        PrintlyElectricityCost,
    )

    # Offerten nach Status gruppiert
    active_quotes = (
        PrintlyQuote.query.filter(PrintlyQuote.status.in_(["draft", "sent"]))
        .order_by(PrintlyQuote.created_at.desc())
        .all()
    )
    closed_quotes = (
        PrintlyQuote.query.filter(
            PrintlyQuote.status.in_(["accepted", "rejected", "invoiced"])
        )
        .order_by(PrintlyQuote.created_at.desc())
        .all()
    )

    # Dropdowns
    customers = (
        PrintlyCustomer.query.filter_by(is_active=True)
        .order_by(PrintlyCustomer.last_name)
        .all()
    )
    companies = (
        PrintlyCompany.query.filter_by(is_active=True)
        .order_by(PrintlyCompany.company_name)
        .all()
    )
    printers = (
        PrintlyPrinter.query.filter_by(is_archived=False)
        .order_by(PrintlyPrinter.name)
        .all()
    )
    work_hours = (
        PrintlyWorkHours.query.filter_by(is_archived=False)
        .order_by(PrintlyWorkHours.name)
        .all()
    )
    overhead_profiles = (
        PrintlyOverheadProfile.query.filter_by(is_active=True)
        .order_by(PrintlyOverheadProfile.name)
        .all()
    )
    filaments = (
        PrintlyFilament.query.filter_by(is_archived=False)
        .order_by(PrintlyFilament.name)
        .all()
    )
    discount_profiles = (
        PrintlyDiscountProfile.query.filter_by(is_active=True)
        .order_by(PrintlyDiscountProfile.name)
        .all()
    )

    # Aktiver Stromtarif
    active_energy = PrintlyElectricityCost.query.filter_by(
        is_active=True, is_current=True
    ).first()

    return {
        "active_quotes": active_quotes,
        "closed_quotes": closed_quotes,
        "customers": customers,
        "companies": companies,
        "printers": printers,
        "work_hours": work_hours,
        "overhead_profiles": overhead_profiles,
        "filaments": filaments,
        "discount_profiles": discount_profiles,
        "active_energy": active_energy,
        "total_active": len(active_quotes),
        "total_closed": len(closed_quotes),
    }


def load_quote_detail_context():
    # Leerer Context – wird nur von der manuellen Route mit quote befüllt
    return load_quote_calculator_context()


def load_customers_context():
    # Firmen
    active_companies = (
        PrintlyCompany.query.filter_by(is_active=True)
        .order_by(PrintlyCompany.company_name)
        .all()
    )
    inactive_companies = (
        PrintlyCompany.query.filter_by(is_active=False)
        .order_by(PrintlyCompany.company_name)
        .all()
    )

    # Privatkunden (ohne Firma)
    active_private = (
        PrintlyCustomer.query.filter_by(is_active=True, company_id=None)
        .order_by(PrintlyCustomer.last_name)
        .all()
    )
    inactive_private = (
        PrintlyCustomer.query.filter_by(is_active=False, company_id=None)
        .order_by(PrintlyCustomer.last_name)
        .all()
    )

    # Alle Firmen für Dropdown (beim Kunden erstellen)
    all_companies = (
        PrintlyCompany.query.filter_by(is_active=True)
        .order_by(PrintlyCompany.company_name)
        .all()
    )

    # Rabattprofile für Dropdowns
    from ..models import PrintlyDiscountProfile

    discount_profiles = PrintlyDiscountProfile.query.filter_by(
        is_active=True, discount_type="discount"
    ).all()

    return {
        "active_companies": active_companies,
        "inactive_companies": inactive_companies,
        "active_private": active_private,
        "inactive_private": inactive_private,
        "all_companies": all_companies,
        "discount_profiles": discount_profiles,
        "total_companies": len(active_companies),
        "total_private": len(active_private),
        "total_contacts": sum(c.contacts.count() for c in active_companies),
    }


def load_printers_context():
    active = (
        PrintlyPrinter.query.filter_by(is_archived=False)
        .order_by(PrintlyPrinter.name)
        .all()
    )
    graveyard = (
        PrintlyPrinter.query.filter_by(is_archived=True)
        .order_by(PrintlyPrinter.name)
        .all()
    )
    active_overhead_profiles = (
        PrintlyOverheadProfile.query.filter_by(is_active=True)
        .order_by(PrintlyOverheadProfile.name)
        .all()
    )
    return {
        "all_printers": active,
        "graveyard_printers": graveyard,
        "overhead_profiles": active_overhead_profiles,
    }


def load_filaments_context():
    active = (
        PrintlyFilament.query.filter_by(is_archived=False)
        .order_by(PrintlyFilament.manufacturer, PrintlyFilament.name)
        .all()
    )
    graveyard = (
        PrintlyFilament.query.filter_by(is_archived=True)
        .order_by(PrintlyFilament.name)
        .all()
    )
    return {
        "all_filaments": active,
        "graveyard_filaments": graveyard,
    }


def load_electricity_costs_context():
    all_costs = PrintlyElectricityCost.query.order_by(
        PrintlyElectricityCost.is_active.desc(), PrintlyElectricityCost.name
    ).all()
    return {"all_energy_costs": all_costs}


def load_working_hours_context():
    active = (
        PrintlyWorkHours.query.filter_by(is_archived=False)
        .order_by(PrintlyWorkHours.cost_per_hour.desc())
        .all()
    )
    graveyard = (
        PrintlyWorkHours.query.filter_by(is_archived=True)
        .order_by(PrintlyWorkHours.name)
        .all()
    )
    return {
        "all_work_hours": active,
        "graveyard_work_hours": graveyard,
    }


def load_overhead_profiles_context():
    active = (
        PrintlyOverheadProfile.query.filter_by(is_active=True)
        .order_by(PrintlyOverheadProfile.name)
        .all()
    )
    inactive = (
        PrintlyOverheadProfile.query.filter_by(is_active=False)
        .order_by(PrintlyOverheadProfile.name)
        .all()
    )
    all_printers = (
        PrintlyPrinter.query.filter_by(is_archived=False)
        .order_by(PrintlyPrinter.name)
        .all()
    )
    return {
        "active_profiles": active,
        "inactive_profiles": inactive,
        "all_printers": all_printers,  # für Verknüpfungs-Dropdown
    }


def load_discounts_and_surcharges_context():
    active_discounts = (
        PrintlyDiscountProfile.query.filter_by(is_active=True, discount_type="discount")
        .order_by(PrintlyDiscountProfile.percentage.desc())
        .all()
    )
    active_surcharges = (
        PrintlyDiscountProfile.query.filter_by(
            is_active=True, discount_type="surcharge"
        )
        .order_by(PrintlyDiscountProfile.percentage.desc())
        .all()
    )
    inactive_profiles = (
        PrintlyDiscountProfile.query.filter_by(is_active=False)
        .order_by(PrintlyDiscountProfile.discount_type, PrintlyDiscountProfile.name)
        .all()
    )
    return {
        "active_discounts": active_discounts,
        "active_surcharges": active_surcharges,
        "inactive_profiles": inactive_profiles,
    }


# ============================================================
# PAGES KONFIGURATION
# ============================================================

PAGES = [
    {
        "id": "dashboard",
        "label": "Dashboard",
        "icon": "bi bi-house",
        "template": "_custom/content/Printly_dashboard.html",
        "route": "/dashboard",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_dashboard_context,
    },
    {
        "id": "quote_calculator",
        "label": "Offerte",
        "icon": "bi bi-file-earmark-text",
        "template": "_custom/content/Quote_calculator.html",
        "route": "/quote_calculator",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_quote_calculator_context,
    },
    {
        "id": "customers",
        "label": "Kunden",
        "icon": "bi bi-people",
        "template": "_custom/content/Customers.html",
        "route": "/customers",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_customers_context,
    },
    {
        "id": "printer",
        "label": "Drucker",
        "icon": "bi bi-printer",
        "template": "_custom/content/Printers.html",
        "route": "/printers",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_printers_context,
    },
    {
        "id": "filament",
        "label": "Filamente",
        "icon": "bi bi-disc",
        "template": "_custom/content/Filaments.html",
        "route": "/filaments",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_filaments_context,
    },
    {
        "id": "electricity_costs",
        "label": "Strom Tarife",
        "icon": "bi bi-lightning-charge",
        "template": "_custom/content/Electricity_Costs.html",
        "route": "/electricity_costs",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_electricity_costs_context,
    },
    {
        "id": "working_hours",
        "label": "Arbeitszeiten",
        "icon": "bi bi-clock",
        "template": "_custom/content/Working_Hours.html",
        "route": "/working_hours",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_working_hours_context,
    },
    {
        "id": "overhead_profiles",
        "label": "Overhead Profile",
        "icon": "bi bi-gear",
        "template": "_custom/content/Overhead_Profiles.html",
        "route": "/overhead_profiles",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_overhead_profiles_context,
    },
    {
        "id": "discounts_and_surcharges",
        "label": "Aufschläge und Rabatte",
        "icon": "bi bi-percent",
        "template": "_custom/content/Discounts_and_Surcharges.html",
        "route": "/discounts_and_surcharges",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_discounts_and_surcharges_context,
    },
    {
        "id": "quote_detail_page",
        "label": "Offerte Detail",
        "icon": "bi bi-file-earmark-text",
        "template": "_custom/content/Quote_detail.html",
        "route": "/quote_detail_placeholder",  # ← unerreichbare Route
        "show_in_sidebar": False,
        "admin_only": False,
        "placeholder": True,
        "context_loader": load_quote_detail_context,
    },
]

PAGES_BY_ID = {page["id"]: page for page in PAGES}
