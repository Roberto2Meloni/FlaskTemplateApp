from flask import Blueprint
from app.logger_manager import AppLogger

blueprint = Blueprint(
    "WasEssen",
    __name__,
    url_prefix="/WasEssen",
    template_folder="templates",
    static_folder="static",
    static_url_path="/WasEssen_static",
)

app_logger = AppLogger("APP-WasEssen")
app_logger.info("Starte App-WasEssen initiierung")
