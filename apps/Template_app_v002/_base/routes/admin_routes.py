"""
Base Admin Routes - Erweitert um Custom Tasks Support
"""

from flask import render_template, request
from flask_login import current_user
from app.decorators import admin_required, enabled_required

# Import aus Parent Package (Template_app_v002/__init__.py)
from ... import blueprint, app_logger, app_config, APP_ROOT

# Import AdminHelper-Klasse
from ..helper_app_function.helper_admin_app import AdminHelper, is_ajax_request

# Import Socket-Manager
from app.socketio_manager import get_socketio_manager

# Import Socket-Funktionen
from ..socketio_events import get_active_sockets, get_socket_count

app_logger.info(f"Starte Admin Routes für {app_config.app_name}")

# ============================================
# INITIALISIERE ADMIN HELPER
# ============================================
admin_helper = AdminHelper(app_config, APP_ROOT)


# ========================================
# ADMIN VIEW ROUTES (nur render_template, keine APIs)
# ========================================


@blueprint.route("/app_settings", methods=["GET"])
@admin_required
def app_settings():
    """Admin-Hauptseite"""
    return render_template(
        "Template_app_v002.html",
        user=current_user,
        # config=app_config, --> ersetzen durch config variable aus root?
        content="app_settings",
        app_config=app_config,
    )


@blueprint.route("/app_settings/app_info", methods=["GET"])
@admin_required
def app_info():
    """App-Informationen"""

    if is_ajax_request():
        return render_template(
            "_base/admin/Template_app_v002_admin_info.html",
            user=current_user,
            config=app_config,
            app_config=app_config,
        )

    return render_template(
        "Template_app_v002.html",
        user=current_user,
        config=app_config,
        content="app_settings",
        settings="app_info",
        app_config=app_config,
    )


@blueprint.route("/app_settings/config", methods=["GET"])
@admin_required
def app_settings_config():
    """App-Konfiguration bearbeiten"""

    app_config_dict = app_config.config  # Nutze direkt .config statt .to_dict()

    if is_ajax_request():
        return render_template(
            "_base/admin/Template_app_v002_admin_config.html",
            user=current_user,
            config=app_config,
            app_config_dict=app_config_dict,
            app_config=app_config,
        )

    return render_template(
        "Template_app_v002.html",
        user=current_user,
        config=app_config,
        content="app_settings",
        settings="config",
        app_config_dict=app_config_dict,
        app_config=app_config,
    )


@blueprint.route("/app_settings/sockets", methods=["GET"])
@admin_required
def app_settings_sockets():
    """Socket-Verbindungen anzeigen"""

    # Hole Socket-Manager für zusätzliche Infos
    try:
        socket_manager = get_socketio_manager()
        online_users_count = socket_manager.get_online_users_count()
    except RuntimeError:
        online_users_count = 0

    # Hole aktive Sockets aus socketio_events
    app_sockets = get_active_sockets()
    print(f"🔌 Socket-Liste: {app_sockets}")

    if is_ajax_request():
        return render_template(
            "_base/admin/Template_app_v002_admin_sockets.html",
            user=current_user,
            config=app_config,
            app_config=app_config,
            active_sockets=app_sockets,
            online_users_count=online_users_count,
        )

    return render_template(
        "Template_app_v002.html",
        user=current_user,
        config=app_config,
        content="app_settings",
        settings="sockets",
        app_config=app_config,
        active_sockets=app_sockets,
        online_users_count=online_users_count,
    )


@blueprint.route("/app_settings/tasks", methods=["GET"])
@admin_required
def app_settings_tasks():
    """
    Task-Verwaltungsseite
    Lädt Tasks aus BEIDEN Schedulern (Base + Custom)
    """
    tasks = []

    try:
        # ✅ Lade Base Tasks
        app_logger.debug("Lade Base Tasks...")
        try:
            from ..tasks import app_scheduler

            jobs = app_scheduler.get_jobs()
            for job in jobs:
                # Filtere nur Jobs dieser App
                if job.id.startswith(app_config.app_name):
                    is_paused = False
                    if hasattr(job, "next_run_time") and job.next_run_time is None:
                        is_paused = True

                    task_info = {
                        "id": job.id,
                        "name": job.name if job.name else job.id,
                        "scheduler": "Base",  # ✅ Kennzeichnung
                        "next_run": (
                            job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                            if job.next_run_time
                            else "Pausiert" if is_paused else "Nicht geplant"
                        ),
                        "trigger": str(job.trigger),
                        "func": (
                            job.func.__name__
                            if hasattr(job.func, "__name__")
                            else "Unbekannt"
                        ),
                        "active": not is_paused,
                    }
                    tasks.append(task_info)

            app_logger.debug(
                f"   └─ {len([t for t in tasks if t['scheduler'] == 'Base'])} Base Tasks geladen"
            )

        except Exception as e:
            app_logger.warning(f"Konnte Base Tasks nicht laden: {e}")

        # ✅ Lade Custom Tasks
        app_logger.debug("Lade Custom Tasks...")
        try:
            # Importiere aus _custom Ordner
            from ..._custom.tasks import app_custom_scheduler

            custom_jobs = app_custom_scheduler.get_jobs()
            for job in custom_jobs:
                # Filtere nur Jobs dieser App
                if job.id.startswith(app_config.app_name):
                    is_paused = False
                    if hasattr(job, "next_run_time") and job.next_run_time is None:
                        is_paused = True

                    task_info = {
                        "id": job.id,
                        "name": job.name if job.name else job.id,
                        "scheduler": "Custom",  # ✅ Kennzeichnung
                        "next_run": (
                            job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                            if job.next_run_time
                            else "Pausiert" if is_paused else "Nicht geplant"
                        ),
                        "trigger": str(job.trigger),
                        "func": (
                            job.func.__name__
                            if hasattr(job.func, "__name__")
                            else "Unbekannt"
                        ),
                        "active": not is_paused,
                    }
                    tasks.append(task_info)

            app_logger.debug(
                f"   └─ {len([t for t in tasks if t['scheduler'] == 'Custom'])} Custom Tasks geladen"
            )

        except Exception as e:
            app_logger.warning(f"Konnte Custom Tasks nicht laden: {e}")

        app_logger.info(f"✅ Gesamt Tasks geladen: {len(tasks)}")

    except Exception as e:
        app_logger.error(f"❌ Fehler beim Laden der Tasks: {str(e)}")

    if is_ajax_request():
        return render_template(
            "_base/admin/Template_app_v002_admin_task.html",
            user=current_user,
            tasks=tasks,
            app_config=app_config,
        )

    return render_template(
        "Template_app_v002.html",
        user=current_user,
        content="app_settings",
        settings="tasks",
        tasks=tasks,
        app_config=app_config,
    )


@blueprint.route("/app_settings/logs", methods=["GET"])
@admin_required
def app_settings_logs():
    """App-Logs anzeigen mit Filteroptionen"""

    # Parameter aus Request
    limit = request.args.get("limit", 500, type=int)
    level_filter = request.args.get("level", None, type=str)
    search_term = request.args.get("search", None, type=str)

    # Begrenze Limit
    if limit > 2000:
        limit = 2000

    # Nutze AdminHelper (dynamisch!)
    app_logs = admin_helper.get_app_logs(
        limit=limit, level_filter=level_filter, search_term=search_term
    )
    log_stats = admin_helper.get_log_statistics()

    if is_ajax_request():
        return render_template(
            "_base/admin/Template_app_v002_admin_logs.html",
            user=current_user,
            config=app_config,
            app_logs=app_logs,
            log_stats=log_stats,
            app_config=app_config,
            current_limit=limit,
            current_level=level_filter,
            current_search=search_term,
        )

    return render_template(
        "Template_app_v002.html",
        user=current_user,
        config=app_config,
        content="app_settings",
        settings="logs",
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

    if is_ajax_request():
        return render_template(
            "_base/admin/Template_app_v002_admin_backup_and_restore.html",
            user=current_user,
            config=app_config,
            app_config=app_config,
        )

    return render_template(
        "Template_app_v002.html",
        user=current_user,
        config=app_config,
        content="app_settings",
        settings="backup_and_restore",
        app_config=app_config,
    )


app_logger.info(f"Ende Admin Routes für {app_config.app_name}")
