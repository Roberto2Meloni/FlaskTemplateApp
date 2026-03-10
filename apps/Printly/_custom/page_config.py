"""
Zentrale Seitenkonfiguration für Printly
Neue Seite hinzufügen = nur hier eintragen!
"""

# ============================================================
# CONTEXT LOADER FUNKTIONEN
# ============================================================


def load_dashboard_context():
    return {}


def load_test_context():
    return {}


# ============================================================
# PAGES KONFIGURATION
# ============================================================

PAGES = [
    {
        "id": "dashboard",
        "label": "Dashboard",
        "icon": "bi-house-door-fill",
        "template": "_custom/content/Printly_dashboard.html",
        "route": "/dashboard",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_dashboard_context,
    },
    {
        "id": "test",
        "label": "TEST",
        "icon": "bi-house-door-fill",
        "template": "_custom/content/Printly_test.html",
        "route": "/test",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_test_context,
    },
]

PAGES_BY_ID = {page["id"]: page for page in PAGES}
