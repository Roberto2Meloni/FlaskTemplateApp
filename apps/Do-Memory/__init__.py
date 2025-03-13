from flask import Blueprint

blueprint = Blueprint(
    "do-memory",
    __name__,
    url_prefix="/do-memory",
    template_folder="templates",
    static_folder="static",
)
