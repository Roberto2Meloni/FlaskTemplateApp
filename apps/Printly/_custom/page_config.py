"""
Zentrale Seitenkonfiguration für Printly
Neue Seite hinzufügen = nur hier eintragen!
"""

from ..models import PrintlyPrinter, PrintlyFilament

# ============================================================
# CONTEXT LOADER FUNKTIONEN
# ============================================================


def load_dashboard_context():
    return {}


def load_test_context():
    return {}


def load_quote_calculator_context():
    return {}


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
    return {"all_printers": active, "graveyard_printers": graveyard}


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
    return {}


def load_working_hours_context():
    return {}


def load_overhead_profiles_context():
    return {}


def load_discounts_and_surcharges_context():
    return {}


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
]

PAGES_BY_ID = {page["id"]: page for page in PAGES}
