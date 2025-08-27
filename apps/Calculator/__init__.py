from flask import Blueprint

blueprint = Blueprint(
    "Calculator",
    __name__,
    url_prefix="/Calculator",
    template_folder="templates",
    static_folder="static",
    static_url_path="/Calculator_static",
)
