from . import blueprint, app_logger
from app.decorators import admin_required, enabled_required
from flask_login import current_user
from app.config import Config
from .app_config import AppConfig


config = Config()
app_config = AppConfig()

app_logger.info(f"Starte App-{app_config.app_name} API")


app_logger.info(f"Ende App-{app_config.app_name} API")
