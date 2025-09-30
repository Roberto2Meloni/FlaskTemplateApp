from flask import Blueprint
from app.logger_manager import AppLogger

blueprint = Blueprint(
    "Einkaufsliste",
    __name__,
    url_prefix="/Einkaufsliste",
    template_folder="templates",
    static_folder="static",
    static_url_path="/Einkaufsliste_static",
)
app_logger = AppLogger("APP-EINKAUFSLISTE")
app_logger.info("Starte App-Einkaufsliste initiierung")
