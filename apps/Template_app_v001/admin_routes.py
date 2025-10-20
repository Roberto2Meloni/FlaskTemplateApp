from . import blueprint, app_logger
from app.decorators import admin_required, enabled_required
from flask_login import current_user
from app.config import Config
from flask import render_template, request
from .helper_app_functions.helper_admin_app import get_app_info, get_app_logs
from .app_config import AppConfig

config = Config()
app_config = AppConfig()
app_logger.info(f"Starte App-{app_config.app_name} admin_routes")


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
    app_infos = get_app_info()

    return render_template(
        "NexusPlayer.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="app_info",
        app_infos=app_infos,
        app_config=app_config,
    )


@blueprint.route("/app_settings/config", methods=["GET"])
@admin_required
def app_settings_config():
    app_infos = get_app_info()
    # Bei AJAX: Nur das Admin-Content-Fragment
    if is_ajax_request():
        return render_template(
            "admin/NexusPlayer_admin_config.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_config=app_config,
        )

    # Normal: Komplette Seite mit Admin-Layout
    return render_template(
        "NexusPlayer.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="config",
        app_infos=app_infos,
        app_config=app_config,
    )


@blueprint.route("/app_settings/sockets", methods=["GET"])
@admin_required
def app_settings_sockets():
    app_infos = get_app_info()
    if is_ajax_request():
        return render_template(
            "admin/NexusPlayer_admin_sockets.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_config=app_config,
        )

    return render_template(
        "NexusPlayer.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="sockets",
        app_infos=app_infos,
        app_config=app_config,
    )


@blueprint.route("/app_settings/tasks", methods=["GET"])
@admin_required
def app_settings_tasks():
    app_infos = get_app_info()
    if is_ajax_request():
        return render_template(
            "admin/NexusPlayer_admin_task.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_config=app_config,
        )

    return render_template(
        "NexusPlayer.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="tasks",
        app_infos=app_infos,
        app_config=app_config,
    )


@blueprint.route("/app_settings/logs", methods=["GET"])
@admin_required
def app_settings_logs():
    app_infos = get_app_info()
    app_logs = get_app_logs()
    if is_ajax_request():
        return render_template(
            "admin/NexusPlayer_admin_logs.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_logs=app_logs,
            app_config=app_config,
        )

    return render_template(
        "NexusPlayer.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="logs",
        app_infos=app_infos,
        app_logs=app_logs,
        app_config=app_config,
    )


@blueprint.route("/app_settings/backup_and_restore", methods=["GET"])
@admin_required
def app_settings_backup_and_restore():
    app_infos = get_app_info()

    if is_ajax_request():
        return render_template(
            "admin/NexusPlayer_admin_backup_and_restore.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_config=app_config,
        )

    return render_template(
        "NexusPlayer.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="logs",
        app_infos=app_infos,
        app_config=app_config,
    )


@blueprint.route("/app_settings/app_info", methods=["GET"])
@admin_required
def app_info():
    app_infos = get_app_info()

    if is_ajax_request():
        return render_template(
            "admin/NexusPlayer_admin_info.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_config=app_config,
        )

    return render_template(
        "NexusPlayer.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="app_info",
        app_infos=app_infos,
        app_config=app_config,
    )


app_logger.info("Ende App-NexusPlayer admin_routes")
