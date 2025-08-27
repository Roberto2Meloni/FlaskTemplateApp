from flask import Blueprint

blueprint = Blueprint(
    "TEST",
    __name__,
    url_prefix="/TEST",
    template_folder="templates",
    static_folder="static",
    static_url_path="/TEST_static",
)
