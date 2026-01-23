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


# Integration der verschiednenen optionalen Extensions

if app_config.socketio_enabled:
    # SocketIO
    pass

if app_config.scheduler_enabled:
    # Scheduler
    pass


# Abschlussmeldung Log eintrag
app_logger.info(f"Ende App-{APP_NAME} v{app_config.app_version}")
