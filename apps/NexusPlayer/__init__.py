from flask import Blueprint
from app.logger_manager import AppLogger

blueprint = Blueprint(
    "NexusPlayer",
    __name__,
    url_prefix="/NexusPlayer",
    template_folder="templates",
    static_folder="static",
    static_url_path="/NexusPlayer_static",
)

app_logger = AppLogger("APP-NEXUSPLAYER")
app_logger.info("Starte App-NexusPlayer initiierung")
