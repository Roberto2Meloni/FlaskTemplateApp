"""
Template_app_v002 Initialization
"""

from flask import Blueprint
from pathlib import Path
from app.logger_manager import AppLogger
from ._base.config.app_config import AppConfig

# Config laden
APP_NAME = Path(__file__).parent.name
APP_ROOT = Path(__file__).parent

app_config = AppConfig(APP_NAME, APP_ROOT)

# Logger
app_logger = AppLogger(app_config.logger_name)
app_logger.info(f"Starte App-{APP_NAME} v{app_config.app_version}")

# Blueprint
blueprint = Blueprint(
    APP_NAME,
    __name__,
    url_prefix=app_config.blueprint_url_prefix,
    template_folder=app_config.blueprint_template_folder,
    static_folder=app_config.blueprint_static_folder,
    static_url_path=app_config.blueprint_static_url_path,
)

app_logger.info(f"Blueprint '{blueprint.name}' registriert")

# Exportiere alles
__all__ = ["blueprint", "app_logger", "app_config", "APP_NAME", "APP_ROOT", "init_app"]


# ============================================
# Routes und Extensions registrieren
# ============================================


def _register_routes():
    """Importiere Routes (intern, nach Blueprint-Erstellung)"""
    from ._base.routes import api_routes, admin_routes, admin_api_routes

    from ._custom.routes import routes, admin_routes

    app_logger.info("Routes registriert")


def _register_extensions():
    """Importiere optionale Extensions"""
    if app_config.socketio_enabled:
        try:
            app_logger.debug(
                f"{app_config.app_name}: starte base socketio_events import"
            )
            from ._base import socketio_events

            app_logger.debug(f"{app_config.app_name}: ende base socketio_events import")

            app_logger.info("SocketIO registriert")
        except ImportError:
            pass
    else:
        app_logger.debug(f"{app_config.app_name}: socketio_disabled")

    if app_config.scheduler_enabled:
        try:
            from ._base import tasks

            app_logger.info("Scheduler registriert")
        except ImportError:
            pass


# Registriere alles beim Import
_register_routes()
_register_extensions()

app_logger.info(f"App-{APP_NAME} erfolgreich initialisiert")


# ============================================
# INIT_APP FUNKTION (für neues System)
# ============================================


def init_app(flask_app, db):
    """
    Initialisiere die App mit Flask und Database

    Args:
        flask_app: Flask Application Instance
        db: SQLAlchemy Database Instance
    """
    app_logger.info(f"init_app() aufgerufen für {APP_NAME}")

    # Blueprint registrieren
    flask_app.register_blueprint(blueprint)

    app_logger.info(f"Blueprint '{blueprint.name}' in Flask App registriert")

    return blueprint
