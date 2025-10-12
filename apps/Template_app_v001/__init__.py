from flask import Blueprint
from app.logger_manager import AppLogger

logger_name = "APP-Template_app_v001"

blueprint = Blueprint(
    "Template_app_v001",
    __name__,
    url_prefix="/Template_app_v001",
    template_folder="templates",
    static_folder="static",
    static_url_path="/Template_app_v001_static",
)

app_logger = AppLogger(logger_name)
app_logger.info("Starte App-Template_app_v001 initiierung")
