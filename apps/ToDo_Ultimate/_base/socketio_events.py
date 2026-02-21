"""
Base SocketIO Events für ToDo_Ultimate
"""

from app import socketio
from flask_socketio import emit, disconnect
from flask_login import current_user
from flask import request
from datetime import datetime
from .. import app_logger, app_config, APP_NAME
from app.socketio_manager import get_socketio_manager

app_logger.info(f"Starte App-{APP_NAME} SocketIO Events")


active_sockets = {}


def get_active_sockets():
    """Gibt alle Base Sockets zurück"""
    return active_sockets


def get_socket_count():
    """Gibt Anzahl aktiver Base Sockets zurück"""
    return len(active_sockets)


# ========================================
# VERBINDUNGS-EVENTS
# ========================================


@socketio.on("connect", namespace=f"/{APP_NAME}")
def handle_connect():
    """Wird ausgelöst wenn ein Client sich verbindet"""
    sid = request.sid
    username = current_user.username if current_user.is_authenticated else "Gast"

    # Speichere Socket-Info
    active_sockets[sid] = {
        "sid": sid,
        "username": username,
        "connected_at": datetime.now().isoformat(),
        "user_id": current_user.id if current_user.is_authenticated else None,
    }

    # Registriere beim globalen SocketIO-Manager
    try:
        socket_manager = get_socketio_manager()
        socket_manager.register_socket(sid, username, APP_NAME)
        app_logger.debug(f"Socket tracked: {sid} - {username}")
    except RuntimeError:
        pass

    app_logger.info(
        f"[{APP_NAME}] App-Socket verbunden: {username} (SID: {sid}) "
        f"[{len(active_sockets)} aktive Verbindungen]"
    )


@socketio.on("disconnect", namespace=f"/{APP_NAME}")
def handle_disconnect():
    """Wird ausgelöst wenn ein Client die Verbindung trennt"""
    sid = request.sid

    # ========================================
    # WICHTIG: Custom Socket Cleanup
    # ========================================
    try:
        # Dynamischer Import um Zirkular-Import zu vermeiden
        import sys

        module_name = f"apps.{APP_NAME}._custom.socketio_events"

        if module_name in sys.modules:
            custom_socketio_module = sys.modules[module_name]
            if hasattr(custom_socketio_module, "cleanup_custom_socket"):
                custom_socketio_module.cleanup_custom_socket(sid)
                app_logger.debug(f"Custom Socket cleanup für {sid}")
    except Exception as e:
        app_logger.debug(f"Custom Socket Cleanup: {e}")

    # Base Socket entfernen
    if sid in active_sockets:
        socket_info = active_sockets.pop(sid)
        app_logger.debug(f"Socket removed: {sid} - {socket_info['username']}")

    # Vom globalen Manager entfernen
    try:
        socket_manager = get_socketio_manager()
        socket_manager.unregister_socket(sid)
    except RuntimeError:
        pass

    app_logger.info(
        f"[{APP_NAME}] App-Socket getrennt: {sid} "
        f"[{len(active_sockets)} aktive Verbindungen]"
    )


# ========================================
# STANDARD EVENTS
# ========================================


@socketio.on("ping", namespace=f"/{APP_NAME}")
def handle_ping(data=None):
    emit(
        "pong",
        {
            "client_sent": (
                data.get("client_sent") if data else None
            ),  # JS Zeit zurückschicken
            "server_time": datetime.now().isoformat(),  # Server Zeit
            "active_connections": len(active_sockets),
        },
    )


@socketio.on("get_socket_info", namespace=f"/{APP_NAME}")
def handle_get_socket_info():
    """Sendet Info über aktuelle Verbindung"""
    sid = request.sid
    socket_info = active_sockets.get(sid, {})

    emit(
        "socket_info_reply",
        {
            "sid": sid,
            "username": socket_info.get("username", "Unbekannt"),
            "connected_at": socket_info.get("connected_at"),
            "total_connections": len(active_sockets),
        },
    )


# ========================================
# DISCONNECT HOOK (für andere Module)
# ========================================


def register_disconnect_hook():
    """
    Registriert einen Disconnect-Hook der auch Custom-Events berücksichtigt
    """

    @socketio.on("disconnect")
    def disconnect_hook():
        """Globaler Disconnect-Hook"""
        sid = request.sid
        app_logger.debug(f"Disconnect hook called for {sid}")

        # Cleanup Custom Sockets
        try:
            import sys

            module_name = f"apps.{APP_NAME}._custom.socketio_events"

            if module_name in sys.modules:
                custom_socketio_module = sys.modules[module_name]
                if hasattr(custom_socketio_module, "cleanup_custom_socket"):
                    custom_socketio_module.cleanup_custom_socket(sid)
        except Exception as e:
            app_logger.debug(f"Custom socket cleanup in hook: {e}")


def remove_socket_connection(sid):
    """
    Entferne Socket aus Tracking
    Wird beim Disconnect aufgerufen
    """
    if sid in active_sockets:
        username = active_sockets[sid].get("username", "Unknown")
        del active_sockets[sid]
        app_logger.debug(f"Socket removed: {sid} - {username}")


# Registriere Hook
register_disconnect_hook()

app_logger.info(f"✅ Disconnect-Hook für {APP_NAME} registriert")
app_logger.info(f"✅ {APP_NAME} Socket-Events registriert")
app_logger.info(f"Ende App-{APP_NAME} SocketIO Events")
