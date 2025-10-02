from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint, app_logger
from app.config import Config
from app.decorators import admin_required, enabled_required
from app import db

# for Debuging
from icecream import ic

# from .models import xx
# from app.admin.models import User@
# from app.helper_functions.helper_db_file import check_if_user_has_admin_rights
# from . import socketio_events

config = Config()
app_logger.info("Starte App-WasEssen Route Initialization")
print("WasEssen Version 0.0.0")


@blueprint.route("/WasEssen", methods=["GET"])
@enabled_required
def WasEssen():
    return render_template(
        "WasEssen.html", user=current_user, config=config
    )


app_logger.info("Starte Ende Route Initialization")
