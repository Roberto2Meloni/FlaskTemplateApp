"""
ToDo_Ultimate Initialization
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

    # ========================================
    # SOCKETIO
    # ========================================
    if app_config.socketio_enabled:
        try:
            app_logger.debug(f"{app_config.app_name}: starte socketio_events import")

            # Base SocketIO Events
            from ._base import socketio_events

            app_logger.debug(f"{app_config.app_name}: base socketio_events geladen")

            # Custom SocketIO Events
            try:
                from ._custom import socketio_events as custom_socketio_events

                app_logger.debug(
                    f"{app_config.app_name}: custom socketio_events geladen"
                )
            except ImportError as e:
                app_logger.debug(
                    f"{app_config.app_name}: keine custom socketio_events: {e}"
                )

            app_logger.info("SocketIO registriert (Base + Custom)")

        except ImportError as e:
            app_logger.warning(f"SocketIO konnte nicht geladen werden: {e}")
    else:
        app_logger.debug(f"{app_config.app_name}: socketio_disabled")

    # ========================================
    # SCHEDULER
    # ========================================
    # ⚠️ WICHTIG: Nur Module importieren, NICHT initialisieren!
    # Die Initialisierung erfolgt in init_app()
    if app_config.scheduler_enabled:
        try:
            # Importiere Module (damit Funktionen verfügbar sind)
            from ._base import tasks
            from ._custom import tasks as custom_tasks  # ✅ Alias wegen Namenskonflikt

            app_logger.info("Scheduler Module geladen (Base + Custom)")
        except ImportError as e:
            app_logger.warning(f"Scheduler Module nicht gefunden: {e}")


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

    # ========================================
    # WICHTIG: Scheduler initialisieren
    # ========================================
    if app_config.scheduler_enabled:
        try:
            # Base Scheduler initialisieren
            from ._base.tasks import init_scheduler

            init_scheduler(flask_app)
            app_logger.info("✅ Base Scheduler initialisiert")
        except Exception as e:
            app_logger.error(f"❌ Fehler beim Initialisieren des Base Schedulers: {e}")
            import traceback

            app_logger.error(traceback.format_exc())

        try:
            # Custom Scheduler initialisieren
            from ._custom.tasks import init_custom_scheduler

            init_custom_scheduler(flask_app)
            app_logger.info("✅ Custom Scheduler initialisiert")
        except Exception as e:
            app_logger.error(
                f"❌ Fehler beim Initialisieren des Custom Schedulers: {e}"
            )
            import traceback

            app_logger.error(traceback.format_exc())

    return blueprint
