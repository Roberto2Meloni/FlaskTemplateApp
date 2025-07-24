from flask import Blueprint

blueprint = Blueprint(
    "Einkaufsliste",
    __name__,
    url_prefix="/Einkaufsliste",
    template_folder="templates",
    static_folder="static",
    static_url_path="/Einkaufsliste_static",
)
