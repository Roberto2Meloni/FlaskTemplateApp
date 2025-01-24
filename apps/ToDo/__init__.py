from flask import Blueprint

blueprint = Blueprint(
    "ToDo",
    __name__,
    url_prefix="/ToDo",
    template_folder="templates",
    static_folder="static",
)
