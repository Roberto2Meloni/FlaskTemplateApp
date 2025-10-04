from flask import Blueprint
from app.logger_manager import AppLogger

blueprint = Blueprint(
    "MyGambler",
    __name__,
    url_prefix="/MyGambler",
    template_folder="templates",
    static_folder="static",
    static_url_path="/MyGambler_static",
)

app_logger = AppLogger("APP-TEMPLATE_APP_V000")
app_logger.info("Starte App-MyGambler initiierung")
