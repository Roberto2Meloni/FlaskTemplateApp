from app import socketio
from flask_socketio import emit
from flask_login import current_user
from flask import request
from datetime import datetime
from . import app_logger
from .app_config import AppConfig
from app.socketio_manager import get_socketio_manager
from ._base.socketio_events import active_sockets

app_logger.info("Starte App-Template_app_v001 SocketIO Events")

app_config = AppConfig()

# ========================================
# SOCKET TRACKING
# ========================================

# Globales Dictionary für alle aktiven Socket-Verbindungen dieser App
# active_sockets, diese wird von base verwendet


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
# Diese wird von base verwendet


# ========================================
# SOCKET EVENT HANDLER
# ========================================


def register_socket_events():
    """
    Registriert app-spezifische Socket-Events
    """
    pass
