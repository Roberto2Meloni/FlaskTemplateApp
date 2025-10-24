from . import blueprint, app_logger
from app.decorators import admin_required
from flask_login import current_user
from flask import jsonify, request
from flask_socketio import disconnect as socketio_disconnect
from app.socketio_manager import get_socketio_manager
from .app_config import AppConfig
import threading

app_config = AppConfig()
app_logger.info(f"Starte App-{app_config.app_name} admin_api_routes")

# Import Socket-Management aus socketio_events
from .socketio_events import active_sockets, remove_socket_connection


# ========================================
# SOCKET MANAGEMENT API ROUTES
# ========================================


@blueprint.route("/admin/api_get_sockets", methods=["GET"])
@admin_required
def api_get_sockets():
    """
    API: Hole aktuelle Socket-Liste
    """
    print("API: Hole aktuelle Socket-Liste")
    try:
        # Hole Socket-Manager Status
        try:
            socket_manager = get_socketio_manager()
            online_users = socket_manager.get_online_users_count()
            user_rooms = socket_manager.user_personal_rooms
        except RuntimeError:
            online_users = 0
            user_rooms = {}

        # Erweitere Socket-Infos mit Online-Status
        sockets_list = []
        for sid, info in active_sockets.items():
            socket_info = info.copy()
            socket_info["is_online"] = info.get("user_id") in user_rooms
            sockets_list.append(socket_info)

        return jsonify(
            {
                "success": True,
                "sockets": sockets_list,
                "total": len(active_sockets),
                "online_users": online_users,
            }
        )
    except Exception as e:
        app_logger.error(f"Fehler beim Abrufen der Sockets: {str(e)}")
        print(f"Fehler beim Abrufen der Sockets: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@blueprint.route("/admin/api_disconnect_socket/<sid>", methods=["POST"])
@admin_required
def api_disconnect_socket(sid):
    """
    API: Trenne spezifische Socket-Verbindung
    """
    try:
        if sid not in active_sockets:
            return jsonify({"success": False, "message": "Socket nicht gefunden"}), 404

        socket_info = active_sockets.get(sid)

        # Trenne Socket-Verbindung über SocketIO
        try:
            socketio_disconnect(sid=sid, namespace="/")
        except Exception as e:
            app_logger.warning(f"Fehler beim Disconnect von {sid}: {e}")

        # Entferne aus Tracking
        remove_socket_connection(sid)

        app_logger.info(
            f"Socket {sid} (User: {socket_info.get('username')}) "
            f"wurde von Admin {current_user.username} getrennt"
        )

        return jsonify({"success": True, "message": "Socket erfolgreich getrennt"})

    except Exception as e:
        app_logger.error(f"Fehler beim Trennen des Sockets {sid}: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@blueprint.route("/admin/api_disconnect_all_sockets", methods=["POST"])
@admin_required
def api_disconnect_all_sockets():
    """
    API: Trenne alle Socket-Verbindungen
    """
    try:
        socket_ids = list(active_sockets.keys())

        disconnected = 0
        errors = []

        for sid in socket_ids:
            try:
                socketio_disconnect(sid=sid, namespace="/")
                remove_socket_connection(sid)
                disconnected += 1
            except Exception as e:
                errors.append(f"Socket {sid}: {str(e)}")
                app_logger.warning(f"Fehler beim Trennen von {sid}: {e}")

        app_logger.info(
            f"Admin {current_user.username} hat {disconnected} Socket(s) getrennt"
        )

        return jsonify(
            {
                "success": True,
                "disconnected": disconnected,
                "errors": errors if errors else None,
                "message": f"{disconnected} Socket-Verbindung(en) getrennt",
            }
        )

    except Exception as e:
        app_logger.error(f"Fehler beim Trennen aller Sockets: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# ========================================
# TASK MANAGEMENT API ROUTES
# ========================================


@blueprint.route("/admin/api_get_tasks", methods=["GET"])
@admin_required
def api_get_tasks():
    """
    API: Hole alle Tasks der App
    """
    try:
        from .tasks import app_scheduler

        tasks = []
        jobs = app_scheduler.get_jobs()

        for job in jobs:
            # Filtere nur Jobs dieser App
            if job.id.startswith(app_config.app_name):
                # Prüfe ob Job pausiert ist
                is_paused = False
                if hasattr(job, "next_run_time") and job.next_run_time is None:
                    is_paused = True

                task_info = {
                    "id": job.id,
                    "name": job.name if job.name else job.id,
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

        app_logger.debug(f"API: {len(tasks)} Tasks gefunden")

        return jsonify({"success": True, "tasks": tasks, "count": len(tasks)})

    except Exception as e:
        app_logger.error(f"Fehler beim Abrufen der Tasks: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


@blueprint.route("/admin/api_pause_task/<task_id>", methods=["POST"])
@admin_required
def api_pause_task(task_id):
    """
    API: Pausiere einen Task
    """
    try:
        from .tasks import app_scheduler

        job = app_scheduler.get_job(task_id)
        if job:
            app_scheduler.pause_job(task_id)
            app_logger.info(
                f"Task {task_id} wurde pausiert von Admin {current_user.username}"
            )

            return jsonify(
                {"success": True, "message": "Task wurde pausiert", "status": "paused"}
            )
        else:
            app_logger.warning(f"Task {task_id} nicht gefunden")
            return jsonify({"success": False, "message": "Task nicht gefunden"}), 404

    except Exception as e:
        app_logger.error(f"Fehler beim Pausieren von Task {task_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Fehler: {str(e)}"}), 500


@blueprint.route("/admin/api_resume_task/<task_id>", methods=["POST"])
@admin_required
def api_resume_task(task_id):
    """
    API: Setze einen pausierten Task fort
    """
    try:
        from .tasks import app_scheduler

        job = app_scheduler.get_job(task_id)
        if job:
            app_scheduler.resume_job(task_id)
            app_logger.info(
                f"Task {task_id} wurde fortgesetzt von Admin {current_user.username}"
            )

            return jsonify(
                {
                    "success": True,
                    "message": "Task wurde fortgesetzt",
                    "status": "active",
                }
            )
        else:
            app_logger.warning(f"Task {task_id} nicht gefunden")
            return jsonify({"success": False, "message": "Task nicht gefunden"}), 404

    except Exception as e:
        app_logger.error(f"Fehler beim Fortsetzen von Task {task_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Fehler: {str(e)}"}), 500


@blueprint.route("/admin/api_run_task/<task_id>", methods=["POST"])
@admin_required
def api_run_task(task_id):
    """
    API: Führe einen Task sofort aus
    """
    try:
        from .tasks import app_scheduler

        job = app_scheduler.get_job(task_id)
        if job:
            app_logger.info(
                f"Task {task_id} wird manuell ausgeführt von Admin {current_user.username}"
            )

            # Führe die Funktion direkt aus
            if hasattr(job, "func"):
                # In einem Thread ausführen, damit die Response nicht blockiert wird
                thread = threading.Thread(
                    target=job.func,
                    args=job.args if hasattr(job, "args") else (),
                    kwargs=job.kwargs if hasattr(job, "kwargs") else {},
                    daemon=True,
                    name=f"Manual_{task_id}",
                )
                thread.start()

                return jsonify({"success": True, "message": "Task wird ausgeführt"})
            else:
                return (
                    jsonify(
                        {"success": False, "message": "Task-Funktion nicht gefunden"}
                    ),
                    500,
                )
        else:
            app_logger.warning(f"Task {task_id} nicht gefunden")
            return jsonify({"success": False, "message": "Task nicht gefunden"}), 404

    except Exception as e:
        app_logger.error(f"Fehler beim Ausführen von Task {task_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Fehler: {str(e)}"}), 500


@blueprint.route("/admin/api_task_info/<task_id>", methods=["GET"])
@admin_required
def api_task_info(task_id):
    """
    API: Hole detaillierte Task-Informationen
    """
    try:
        from .tasks import app_scheduler

        job = app_scheduler.get_job(task_id)
        if job:
            is_paused = False
            if hasattr(job, "next_run_time") and job.next_run_time is None:
                is_paused = True

            task_info = {
                "id": job.id,
                "name": job.name if job.name else job.id,
                "next_run": (
                    job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                    if job.next_run_time
                    else "Pausiert" if is_paused else "Nicht geplant"
                ),
                "trigger": str(job.trigger),
                "func": (
                    job.func.__name__ if hasattr(job.func, "__name__") else "Unbekannt"
                ),
                "active": not is_paused,
                "args": str(job.args) if hasattr(job, "args") else "",
                "kwargs": str(job.kwargs) if hasattr(job, "kwargs") else "",
            }

            return jsonify({"success": True, "task": task_info})
        else:
            return jsonify({"success": False, "message": "Task nicht gefunden"}), 404

    except Exception as e:
        app_logger.error(f"Fehler beim Abrufen der Task-Info {task_id}: {str(e)}")
        return jsonify({"success": False, "message": f"Fehler: {str(e)}"}), 500


# ========================================
# CONFIG MANAGEMENT API
# ========================================


@blueprint.route("/admin/api_save_config", methods=["POST"])
@admin_required
def api_save_config():
    """
    API: Speichere App-Konfiguration
    """
    from .helper_app_functions.helper_admin_app import convert_value

    try:
        current_config = app_config.to_dict()
        new_config = {}

        # Verarbeite Form-Daten
        for key in request.form.keys():
            if key == "csrf_token" or key == "app_name":
                continue

            value = request.form.get(key)

            # Verschachtelte Werte
            if "[" in key and "]" in key:
                parent_key = key.split("[")[0]
                child_key = key.split("[")[1].rstrip("]")

                if parent_key not in new_config:
                    new_config[parent_key] = {}

                original_value = current_config.get(parent_key, {}).get(child_key)
                new_config[parent_key][child_key] = convert_value(value, original_value)
            else:
                new_config[key] = convert_value(value, current_config.get(key))

        # Checkboxen
        for key, value in current_config.items():
            if key == "app_name":
                continue

            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, bool):
                        form_key = f"{key}[{sub_key}]"
                        if form_key not in request.form:
                            if key not in new_config:
                                new_config[key] = {}
                            new_config[key][sub_key] = False
            elif isinstance(value, bool):
                if key not in request.form:
                    new_config[key] = False

        app_config.update_config(new_config, skip_app_name=True)
        app_config.refresh()

        app_logger.info(f"App-Konfiguration gespeichert von {current_user.username}")

        return jsonify(
            {"success": True, "message": "Konfiguration erfolgreich gespeichert"}
        )

    except Exception as e:
        app_logger.error(f"Fehler beim Speichern der Config: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


app_logger.info(f"Ende App-{app_config.app_name} admin_api_routes")
