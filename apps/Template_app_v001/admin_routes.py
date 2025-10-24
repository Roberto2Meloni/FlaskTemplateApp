from . import blueprint, app_logger
from app.decorators import admin_required, enabled_required
from flask_login import current_user
from app.config import Config
from flask import render_template, request
from .helper_app_functions.helper_admin_app import (
    get_app_info,
    get_app_logs,
    is_ajax_request,
)
from .app_config import AppConfig
from app.socketio_manager import get_socketio_manager
from .tasks import get_all_tasks
from .helper_app_functions.helper_admin_app import get_log_statistics

# Globale Variablen
config = Config()
app_config = AppConfig()
app_logger.info(f"Starte App-{app_config.app_name} admin_routes")

# Import Socket-Funktionen aus socketio_events (für Views)
from .socketio_events import get_active_sockets, get_socket_count


# ========================================
# ADMIN VIEW ROUTES (nur render_template, keine APIs)
# ========================================


@blueprint.route("/app_settings", methods=["GET"])
@admin_required
def app_settings():
    """Admin-Hauptseite"""
    app_infos = get_app_info()
    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="app_info",
        app_infos=app_infos,
        app_config=app_config,
    )


@blueprint.route("/app_settings/app_info", methods=["GET"])
@admin_required
def app_info():
    """App-Informationen"""
    app_infos = get_app_info()

    if is_ajax_request():
        return render_template(
            "admin/Template_app_v001_admin_info.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_config=app_config,
        )

    return render_template(
        "Template_app_v001.html",
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
    """App-Konfiguration bearbeiten"""
    app_infos = get_app_info()
    app_config_dict = app_config.to_dict()

    if is_ajax_request():
        return render_template(
            "admin/Template_app_v001_admin_config.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_config_dict=app_config_dict,
            app_config=app_config,
        )

    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="config",
        app_infos=app_infos,
        app_config_dict=app_config_dict,
        app_config=app_config,
    )


@blueprint.route("/app_settings/sockets", methods=["GET"])
@admin_required
def app_settings_sockets():
    """Socket-Verbindungen anzeigen"""
    app_infos = get_app_info()

    # Hole Socket-Manager für zusätzliche Infos
    try:
        socket_manager = get_socketio_manager()
        online_users_count = socket_manager.get_online_users_count()
    except RuntimeError:
        online_users_count = 0

    # Hole aktive Sockets aus socketio_events
    app_sockets = get_active_sockets()

    if is_ajax_request():
        return render_template(
            "admin/Template_app_v001_admin_sockets.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_config=app_config,
            active_sockets=app_sockets,
            online_users_count=online_users_count,
        )

    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="sockets",
        app_infos=app_infos,
        app_config=app_config,
        active_sockets=app_sockets,
        online_users_count=online_users_count,
    )


@blueprint.route("/app_settings/tasks", methods=["GET"])
@admin_required
def app_settings_tasks():
    """Task-Verwaltung - Zeigt alle aktiven Tasks"""
    app_infos = get_app_info()
    tasks = get_all_tasks()

    if is_ajax_request():
        return render_template(
            "admin/Template_app_v001_admin_task.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_config=app_config,
            tasks=tasks,
        )

    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="tasks",
        app_infos=app_infos,
        app_config=app_config,
        tasks=tasks,
    )


@blueprint.route("/app_settings/logs", methods=["GET"])
@admin_required
def app_settings_logs():
    """
    App-Logs anzeigen mit Filteroptionen
    """
    # Parameter aus Request
    limit = request.args.get("limit", 500, type=int)
    level_filter = request.args.get("level", None, type=str)
    search_term = request.args.get("search", None, type=str)

    # Begrenze Limit auf Maximum
    if limit > 2000:
        limit = 2000

    app_infos = get_app_info()
    app_logs = get_app_logs(
        limit=limit, level_filter=level_filter, search_term=search_term
    )
    log_stats = get_log_statistics()

    if is_ajax_request():
        return render_template(
            "admin/Template_app_v001_admin_logs.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_logs=app_logs,
            log_stats=log_stats,
            app_config=app_config,
            current_limit=limit,
            current_level=level_filter,
            current_search=search_term,
        )

    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="logs",
        app_infos=app_infos,
        app_logs=app_logs,
        log_stats=log_stats,
        app_config=app_config,
        current_limit=limit,
        current_level=level_filter,
        current_search=search_term,
    )


@blueprint.route("/app_settings/backup_and_restore", methods=["GET"])
@admin_required
def app_settings_backup_and_restore():
    """Backup & Restore"""
    app_infos = get_app_info()

    if is_ajax_request():
        return render_template(
            "admin/Template_app_v001_admin_backup_and_restore.html",
            user=current_user,
            config=config,
            app_infos=app_infos,
            app_config=app_config,
        )

    return render_template(
        "Template_app_v001.html",
        user=current_user,
        config=config,
        content="app_settings",
        settings="backup_and_restore",
        app_infos=app_infos,
        app_config=app_config,
    )


app_logger.info(f"Ende App-{app_config.app_name} admin_routes")
