from . import blueprint, app_logger
from app.decorators import admin_required, enabled_required
from flask_login import current_user
from app.config import Config


app_logger.info("Starte App-Template_app_v001 API")
config = Config()


app_logger.info("Ende App-Template_app_v001 API")
