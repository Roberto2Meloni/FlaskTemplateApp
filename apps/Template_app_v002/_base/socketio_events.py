from app import socketio
from flask_socketio import emit
from flask_login import current_user
from flask import request
from datetime import datetime
from .. import app_logger, app_config
from app.socketio_manager import get_socketio_manager

app_logger.info(f"Starte App-{app_config.app_name} SocketIO Events")

# ========================================
# SOCKET TRACKING
# ========================================

# Globales Dictionary für alle aktiven Socket-Verbindungen dieser App
active_sockets = {}


def track_socket_connection(sid, user_info):
    """
    Tracke Socket-Verbindung
    Wird aufgerufen wenn ein Client sich mit der App verbindet
    """
    active_sockets[sid] = {
        "sid": sid,
        "user_id": user_info.get("user_id"),
        "username": user_info.get("username"),
        "connected_at": user_info.get("connected_at"),
        "app_name": user_info.get("app_name", app_config.app_name),
    }
    app_logger.debug(f"Socket tracked: {sid} - {user_info.get('username')}")


def remove_socket_connection(sid):
    """
    Entferne Socket aus Tracking
    Wird beim Disconnect aufgerufen
    """
    if sid in active_sockets:
        username = active_sockets[sid].get("username", "Unknown")
        del active_sockets[sid]
        app_logger.debug(f"Socket removed: {sid} - {username}")


def get_active_sockets():
    """
    Gibt alle aktiven Socket-Verbindungen zurück
    """
    return active_sockets.copy()


def get_socket_count():
    """
    Gibt die Anzahl aktiver Sockets zurück
    """
    return len(active_sockets)


# ========================================
# DISCONNECT HOOK FÜR SOCKETIO MANAGER
# ========================================


def disconnect_hook_handler(request_sid, user_data):
    """
    Disconnect Hook für SocketIOManager
    Wird automatisch aufgerufen wenn eine Verbindung getrennt wird
    """
    remove_socket_connection(request_sid)
    app_logger.debug(f"Disconnect hook called for {request_sid}")


# Registriere Disconnect Hook beim SocketIOManager
try:
    socket_manager = get_socketio_manager()
    socket_manager.register_disconnect_hook(
        app_name=app_config.app_name, hook_function=disconnect_hook_handler
    )
    app_logger.info(f"✅ Disconnect-Hook für {app_config.app_name} registriert")
except RuntimeError:
    app_logger.warning(
        "⚠️ SocketIOManager noch nicht initialisiert - Hook wird später registriert"
    )


# ========================================
# SOCKET EVENT HANDLER
# ========================================


def register_socket_events():
    """
    Registriert app-spezifische Socket-Events
    """

    # NEU: Dynamische Event-Namen
    connect_event = f"{app_config.app_name}_connect"
    connected_event = f"{app_config.app_name}_connected"
    ping_event = f"{app_config.app_name}_ping"
    pong_event = f"{app_config.app_name}_pong"
    disconnect_event = f"{app_config.app_name}_disconnect"

    @socketio.on(connect_event)
    def handle_app_connect(data=None):
        """
        App-spezifisches Connect Event
        Wird vom Client gesendet wenn er sich mit der App verbindet
        """
        sid = request.sid

        user_info = {
            "sid": sid,
            "user_id": current_user.id if current_user.is_authenticated else None,
            "username": (
                current_user.username
                if current_user.is_authenticated
                else f"Guest_{sid[:6]}"
            ),
            "connected_at": datetime.now().isoformat(),
            "app_name": app_config.app_name,
        }

        # Tracke die Verbindung
        track_socket_connection(sid, user_info)

        app_logger.info(
            f"App-Socket verbunden: {user_info['username']} (SID: {sid}) "
            f"[{get_socket_count()} aktive Verbindungen]"
        )

        # Sende Bestätigung an Client
        emit(
            connected_event,
            {
                "sid": sid,
                "username": user_info["username"],
                "app": app_config.app_name,
                "message": f"Verbunden mit {app_config.app_name}",
                "active_connections": get_socket_count(),
            },
        )

    @socketio.on(connect_event)
    def handle_app_ping():
        """
        App-spezifischer Ping für Connection-Health-Check
        """
        emit(
            connected_event,
            {
                "timestamp": datetime.now().isoformat(),
                "app": app_config.app_name,
                "active_connections": get_socket_count(),
            },
        )

    @socketio.on(connect_event)
    def handle_app_disconnect():
        """
        App-spezifisches Disconnect Event
        Optional: Explizites Disconnect vom Client
        """
        sid = request.sid
        remove_socket_connection(sid)

        app_logger.info(
            f"App-Socket getrennt: {sid} " f"[{get_socket_count()} aktive Verbindungen]"
        )

    # ===== BEISPIEL: Weitere App-spezifische Events =====

    # @socketio.on('Template_app_v001_custom_event')
    # def handle_custom_event(data):
    #     """
    #     Beispiel für ein eigenes Socket-Event
    #     """
    #     app_logger.info(f"Custom Event empfangen: {data}")
    #
    #     # Verarbeite Event...
    #
    #     emit(connected_event, {
    #         'status': 'ok',
    #         'data': data
    #     })

    app_logger.info(f"✅ {app_config.app_name} Socket-Events registriert")
    return {
        connect_event: handle_app_connect,
        ping_event: handle_app_ping,
        disconnect_event: handle_app_disconnect,
    }


# Registriere Events beim Import
# Registriere Events beim Import und speichere sie
SOCKETIO_EVENTS = register_socket_events()

app_logger.info(f"Ende App-{app_config.app_name} SocketIO Events")
