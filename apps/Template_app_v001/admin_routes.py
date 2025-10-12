from . import blueprint, app_logger
from app.decorators import admin_required, enabled_required
from flask_login import current_user
from app.config import Config
from flask import render_template, request

app_logger.info("Starte App-Template_app_v001 admin_routes")
config = Config()


def is_ajax_request():
    """
    Prüft ob der Request von fetch/JavaScript kommt
    """
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


# ========================================
# VOLLSTÄNDIGE ADMIN-SEITEN
# Diese laden das komplette Layout
# ========================================


@blueprint.route("/app_settings", methods=["GET"])
@admin_required
def app_settings():
    # Admin-Hauptseite lädt IMMER komplett (mit beiden Sidebars)
    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="config",
    )


@blueprint.route("/app_settings/config", methods=["GET"])
@admin_required
def app_settings_config():
    # Bei AJAX: Nur das Admin-Content-Fragment
    if is_ajax_request():
        return render_template(
            "admin/Template_app_v001_admin_config.html",
            user=current_user,
            config=config,
        )

    # Normal: Komplette Seite mit Admin-Layout
    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="config",
    )


@blueprint.route("/app_settings/sockets", methods=["GET"])
@admin_required
def app_settings_sockets():
    if is_ajax_request():
        return render_template(
            "admin/Template_app_v001_admin_sockets.html",
            user=current_user,
            config=config,
        )

    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="sockets",
    )


@blueprint.route("/app_settings/tasks", methods=["GET"])
@admin_required
def app_settings_tasks():
    if is_ajax_request():
        return render_template(
            "admin/Template_app_v001_admin_task.html", user=current_user, config=config
        )

    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="tasks",
    )


@blueprint.route("/app_settings/logs", methods=["GET"])
@admin_required
def app_settings_logs():
    if is_ajax_request():
        return render_template(
            "admin/Template_app_v001_admin_logs.html", user=current_user, config=config
        )

    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="logs",
    )


app_logger.info("Ende App-Template_app_v001 admin_routes")
