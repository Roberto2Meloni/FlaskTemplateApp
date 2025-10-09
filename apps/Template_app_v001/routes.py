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
# from . import api

config = Config()
app_logger.info("Starte App-Template_app_v001 Route Initialization")
print("Template_app_v001 Version 0.0.0")


@blueprint.route("/Template_app_v001_index", methods=["GET"])
@enabled_required
def Template_app_v001_index():
    return render_template("Template_app_v001.html", user=current_user, config=config)


@blueprint.route("/app_settings", methods=["GET"])
@enabled_required
def app_settings():
    return render_template(
        "Template_app_v001_app_settings.html", user=current_user, config=config
    )


app_logger.info("Starte Ende Route Initialization")
