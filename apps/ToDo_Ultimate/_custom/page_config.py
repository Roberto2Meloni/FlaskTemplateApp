"""
Zentrale Seitenkonfiguration für ToDo_Ultimate
Neue Seite hinzufügen = nur hier eintragen!
"""

# ============================================================
# CONTEXT LOADER FUNKTIONEN
# ============================================================


def load_dashboard_context():
    return {}


def load_todos_context():
    # from ..models import ToDo
    # todos = ToDo.query.filter_by(user_id=current_user.id).all()
    # return {"todos": todos}
    return {"todos": []}  # ← Platzhalter bis Model existiert


def load_pipeline_context():
    return {}  # ← Platzhalter


def load_archive_context():
    return {}  # ← Platzhalter


# ============================================================
# PAGES KONFIGURATION
# ============================================================

PAGES = [
    {
        "id": "dashboard",
        "label": "Dashboard",
        "icon": "bi-house-door-fill",
        "template": "_custom/content/ToDo_Ultimate_dashboard.html",
        "route": "/dashboard",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_dashboard_context,
    },
    {
        "id": "my_todos",
        "label": "Meine ToDo's",
        "icon": "bi-journal-text",
        "template": "_custom/content/ToDo_Ultimate_my_todos.html",
        "route": "/my_todos",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": False,
        "context_loader": load_todos_context,
    },
    {
        "id": "my_pipeline",
        "label": "Pipeline",
        "icon": "bi-kanban",
        "template": None,
        "route": "/my_pipeline",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": True,
        "context_loader": load_pipeline_context,
    },
    {
        "id": "my_archive",
        "label": "Archiviert",
        "icon": "bi-archive",
        "template": None,
        "route": "/my_archive",
        "show_in_sidebar": True,
        "admin_only": False,
        "placeholder": True,
        "context_loader": load_archive_context,
    },
]

PAGES_BY_ID = {page["id"]: page for page in PAGES}
