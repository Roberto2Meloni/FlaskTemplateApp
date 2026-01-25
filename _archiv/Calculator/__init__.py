from flask import Blueprint
from app.logger_manager import AppLogger

blueprint = Blueprint(
    "Calculator",
    __name__,
    url_prefix="/Calculator",
    template_folder="templates",
    static_folder="static",
    static_url_path="/Calculator_static",
)

app_logger = AppLogger("APP-CALCULATOR")
app_logger.info("Starte APP-CALCULATOR initiierung")
