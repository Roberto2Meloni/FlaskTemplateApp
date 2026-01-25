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

# Integration der Routes (WICHTIG: Nach Blueprint-Erstellung!)
from ._base.routes import api_routes, admin_routes, admin_api_routes
from ._custom.routes import routes

# Integration der verschiedenen optionalen Extensions
if app_config.socketio_enabled:
    # SocketIO
    from ._base.socketio_events import SOCKETIO_EVENTS
else:
    SOCKETIO_EVENTS = {}

if app_config.scheduler_enabled:
    # Scheduler
    pass


# ============================================================================
# INIT_APP() für Flask-Integration
# ============================================================================
def init_app(flask_app, database):
    """
    Initialisiert die App im Flask-Kontext

    Args:
        flask_app: Flask application instance
        database: SQLAlchemy database instance

    Returns:
        bool: True wenn erfolgreich, False bei Fehler
    """
    try:
        app_logger.info(f"init_app() aufgerufen für {APP_NAME}")

        # 1. Blueprint registrieren
        flask_app.register_blueprint(blueprint)
        app_logger.info(f"✅ Blueprint '{APP_NAME}' registriert")

        # 2. Models importieren (falls vorhanden)
        try:
            from . import models

            app_logger.info("✅ Models importiert")
        except ImportError:
            app_logger.info("ℹ️  Keine models.py gefunden (optional)")

        app_logger.info(f"✅ {APP_NAME} erfolgreich initialisiert via init_app()")
        return True

    except Exception as e:
        app_logger.error(f"❌ Fehler in init_app() von {APP_NAME}: {e}")
        import traceback

        app_logger.error(traceback.format_exc())
        return False


# ============================================================================
# SOCKETIO EVENTS EXPORT
# ============================================================================
def get_socketio_events():
    """
    Gibt Socket.IO Events zurück für externe Registrierung

    Returns:
        dict: Event-Handlers (leer wenn socketio_enabled=False)
    """
    if app_config.socketio_enabled:
        return SOCKETIO_EVENTS
    return {}


# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    "blueprint",
    "init_app",
    "get_socketio_events",
    "APP_NAME",
    "app_config",
    "app_logger",
]

# Abschlussmeldung Log eintrag
app_logger.info(f"Ende App-{APP_NAME} v{app_config.app_version}")
