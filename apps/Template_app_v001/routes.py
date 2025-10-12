from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import (
    api_routes,
    blueprint,
    app_logger,
    socketio_events,
    admin_routes,
)
from app.config import Config
from app.decorators import admin_required, enabled_required

# from app import db

config = Config()
app_logger.info("Starte App-Template_app_v001 Route Initialization")
print("Template_app_v001 Version 0.0.0")


def is_ajax_request():
    """
    Prüft ob der Request von fetch/JavaScript kommt
    """
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@blueprint.route("/", methods=["GET"])
@blueprint.route("/Template_app_v001_index", methods=["GET"])
@enabled_required
def Template_app_v001_index():
    return render_template(
        "Template_app_v001.html", user=current_user, config=config, content="dashboard"
    )


@blueprint.route("/dashboard", methods=["GET"])
@enabled_required
def dashboard():
    # Bei AJAX: Nur Content
    if is_ajax_request():
        return render_template(
            "content/Template_app_v001_dashboard.html", user=current_user, config=config
        )

    # Normal: Komplette Seite
    return render_template(
        "Template_app_v001.html", user=current_user, config=config, content="dashboard"
    )


@blueprint.route("/page_01", methods=["GET"])
@enabled_required
def page_01():
    if is_ajax_request():
        return render_template(
            "content/Template_app_v001_page_01.html", user=current_user, config=config
        )

    return render_template(
        "Template_app_v001.html", user=current_user, config=config, content="page_01"
    )


@blueprint.route("/page_02", methods=["GET"])
@enabled_required
def page_02():
    if is_ajax_request():
        return render_template(
            "content/Template_app_v001_page_02.html", user=current_user, config=config
        )

    return render_template(
        "Template_app_v001.html", user=current_user, config=config, content="page_02"
    )


@blueprint.route("/page_03", methods=["GET"])
@enabled_required
def page_03():
    if is_ajax_request():
        return render_template(
            "content/Template_app_v001_page_03.html", user=current_user, config=config
        )

    return render_template(
        "Template_app_v001.html", user=current_user, config=config, content="page_03"
    )


app_logger.info("Ende Route Initialization")
