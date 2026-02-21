"""
Custom SocketIO Events für Template_app_v002
"""

from app import socketio
from flask_socketio import emit
from flask import request
from .. import app_logger, APP_NAME

app_logger.info(f"Starte Custom SocketIO Events für {APP_NAME}")

NAMESPACE = f"/{APP_NAME}"

# ========================================
# HELLO EVENT
# ========================================


@socketio.on("hello", namespace=NAMESPACE)
def handle_hello():
    """
    Client sendet: hello
    Server antwortet: world
    """
    sid = request.sid
    app_logger.info(f"[{APP_NAME}] Hello Event von {sid}")

    emit("world", {"message": "Hello World!"})


# ========================================
# CLEANUP HOOK (wird von base aufgerufen)
# ========================================


def cleanup_custom_socket(sid):
    """
    Wird beim Disconnect vom base_socketio_events aufgerufen.
    Hier Custom-Cleanup wenn nötig.
    """
    app_logger.debug(f"[{APP_NAME}] Custom Socket Cleanup für {sid}")


app_logger.info(f"✅ Custom SocketIO Events registriert auf Namespace: {NAMESPACE}")
