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

# Aktung die Dateien der Templates müssen immer den Prefix der App haben
# MyGambler_alles_in_kelin_name_der_seite.html


config = Config()
app_logger.info("Starte App-MyGambler Route Initialization")
print("MyGambler Version 0.0.0")


@blueprint.route("/MyGambler_index", methods=["GET"])
@enabled_required
def MyGambler_index():
    return render_template("MyGambler.html", user=current_user, config=config)


@blueprint.route("/dashboard", methods=["GET"])
@enabled_required
def dashboard():
    return render_template("MyGambler_dashboard.html", user=current_user, config=config)


@blueprint.route("/slot_maschine", methods=["GET"])
@enabled_required
def slot_maschine():
    print("slot_maschine")
    return render_template(
        "MyGambler_slot_maschine.html", user=current_user, config=config
    )


@blueprint.route("/app_settings", methods=["GET"])
@admin_required
def app_settings():
    return render_template(
        "MyGambler_app_settings.html", user=current_user, config=config
    )


app_logger.info("Starte Ende Route Initialization")
