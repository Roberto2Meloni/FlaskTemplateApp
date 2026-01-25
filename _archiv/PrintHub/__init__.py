from flask import Blueprint
from app.logger_manager import AppLogger

blueprint = Blueprint(
    "PrintHub",
    __name__,
    url_prefix="/PrintHub",
    template_folder="templates",
    static_folder="static",
    static_url_path="/PrintHub_static",
)
app_logger = AppLogger("APP-PrintHub")
app_logger.info("Starte PrintHub initiierung")
