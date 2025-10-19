import os
from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint, app_logger, api_routes, admin_routes
from app.config import Config
from app.decorators import admin_required, enabled_required
from app import db
from .helper_app_functions.helper_app_functions import (
    get_both,
    get_all_playlists_json,
)
from .app_config import AppConfig
from . import tasks


# for Debuging
from icecream import ic

# from .models import xx
# from app.admin.models import User@
# from app.helper_functions.helper_db_file import check_if_user_has_admin_rights

config = Config()
app_config = AppConfig()

app_logger.info("Starte App-NexusPlayer Route Initialization")
print("NexusPlayer Version 0.0.0")


def is_ajax_request():
    """
    Prüft ob der Request von fetch/JavaScript kommt
    """
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@blueprint.route("/", methods=["GET"])
@blueprint.route("/NexusPlayer_index", methods=["GET"])
@enabled_required
def NexusPlayer_index():
    return render_template(
        "NexusPlayer.html", user=current_user, config=config, content="dashboard"
    )


@blueprint.route("/dashboard", methods=["GET"])
@enabled_required
def dashboard():

    # Bei AJAX: Nur Content
    if is_ajax_request():
        return render_template(
            "content/NexusPlayer_Dashboard.html",
            user=current_user,
            config=config,
            content="dashboard",
        )

    return render_template(
        "NexusPlayer.html",
        user=current_user,
        config=config,
        content="dashboard",
    )


# Alles zum Theeme Files


@blueprint.route("/files", methods=["GET"])
@enabled_required
def files():
    full_architecture, simpel_architecture = get_both()
    # Bei AJAX: Nur Content
    if is_ajax_request():
        return render_template(
            "content/NexusPlayer_files.html",
            user=current_user,
            config=config,
            content="files",
            full_architecture=full_architecture,
            simpel_architecture=simpel_architecture,
        )

    return render_template(
        "NexusPlayer.html",
        user=current_user,
        config=config,
        full_architecture=full_architecture,
        simpel_architecture=simpel_architecture,
        content="files",
    )


@blueprint.route("/playlists", methods=["GET"])
@enabled_required
def playlists():
    all_playlists_json = get_all_playlists_json()
    print(all_playlists_json)
    if is_ajax_request():
        return render_template(
            "content/NexusPlayer_Playlists.html",
            user=current_user,
            config=config,
            content="playlists",
            all_playlists_json=all_playlists_json,
        )

    return render_template(
        "NexusPlayer.html",
        user=current_user,
        config=config,
        content="playlists",
        all_playlists_json=all_playlists_json,
    )


@blueprint.route("/devices", methods=["GET"])
@enabled_required
def devices():

    if is_ajax_request():
        return render_template(
            "content/Template_app_v001_dashboard.html", user=current_user, config=config
        )
    return render_template(
        "content/NexusPlayer_Devices.html", user=current_user, config=config
    )


app_logger.info("Ende App-NexusPlayer Route Initialization")
