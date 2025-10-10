from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import api_routes, blueprint, app_logger, content_routes, socketio_events
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


@blueprint.route("/dashboard", methods=["GET"])
@enabled_required
def dashboard():
    return render_template(
        "Template_app_v001.html", user=current_user, config=config, content="dashboard"
    )


@blueprint.route("/page_01", methods=["GET"])
@enabled_required
def page_01():
    return render_template(
        "Template_app_v001.html", user=current_user, config=config, content="page_01"
    )


@blueprint.route("/page_02", methods=["GET"])
@enabled_required
def page_02():
    return render_template(
        "Template_app_v001.html", user=current_user, config=config, content="page_02"
    )


@blueprint.route("/page_03", methods=["GET"])
@enabled_required
def page_03():
    return render_template(
        "Template_app_v001.html", user=current_user, config=config, content="page_03"
    )


@blueprint.route("/app_settings", methods=["GET"])
@admin_required
def app_settings():
    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
    )


app_logger.info("Starte Ende Route Initialization")
