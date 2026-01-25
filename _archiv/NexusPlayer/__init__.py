from flask import Blueprint
from app.logger_manager import AppLogger

logger_name = "APP-NexusPlayer"
app_name = "NexusPlayer"

blueprint = Blueprint(
    app_name,
    __name__,
    url_prefix="/NexusPlayer",
    template_folder="templates",
    static_folder="static",
    static_url_path="/NexusPlayer_static",
)

app_logger = AppLogger(logger_name)
app_logger.info("Starte App-NexusPlayer initiierung")
