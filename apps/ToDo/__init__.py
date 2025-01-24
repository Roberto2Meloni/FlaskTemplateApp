from flask import Blueprint

blueprint = Blueprint(
    "todo",
    __name__,
    url_prefix="/todo",
    template_folder="templates",
    static_folder="static",
)
