from flask import Blueprint

blueprint = Blueprint(
    "einkaufsliste",
    __name__,
    url_prefix="/einkaufsliste",
    template_folder="templates",
    static_folder="static",
)
