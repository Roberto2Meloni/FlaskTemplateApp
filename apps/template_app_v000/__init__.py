from flask import Blueprint
from app.logger_manager import AppLogger

blueprint = Blueprint(
    "Template_app_v000",
    __name__,
    url_prefix="/Template_app_v000",
    template_folder="templates",
    static_folder="static",
    static_url_path="/Template_app_v000_static",
)

app_logger = AppLogger("APP-TEMPLATE_APP_V000")
app_logger.info("Starte App-Template_app_v000 initiierung")
