from . import blueprint, app_logger
from app.decorators import admin_required
from flask_login import current_user
from flask import jsonify
from flask_socketio import disconnect as socketio_disconnect
from app.socketio_manager import get_socketio_manager
from .app_config import AppConfig

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
# CONFIG MANAGEMENT API
# ========================================


@blueprint.route("/admin/api_save_config", methods=["POST"])
@admin_required
def api_save_config():
    """
    API: Speichere App-Konfiguration
    (Diese Route kann aus admin_routes hierher verschoben werden)
    """
    from flask import request
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
