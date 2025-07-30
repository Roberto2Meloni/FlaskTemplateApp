from flask import Blueprint

blueprint = Blueprint(
    "NexusPlayer",
    __name__,
    url_prefix="/NexusPlayer",
    template_folder="templates",
    static_folder="static",
    static_url_path="/NexusPlayer_static",
)
