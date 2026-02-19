"""
Custom SocketIO Events für Template_app_v002
SUPER EINFACHE VERSION
"""

from app import socketio
from flask_socketio import emit
from flask import request
from .. import app_logger, app_config, APP_NAME
from .._base.socketio_events import active_sockets


app_logger.info(f"Starte Custom SocketIO Events für {APP_NAME}")


# ========================================
# HELLO EVENT
# ========================================
@socketio.on("hello")
def handle_hello():
    """
    Client sendet: hello
    Server antwortet: world
    """
    sid = request.sid

    app_logger.info(f"🔄 Hello Event von {sid}")

    # Antworte mit "world"
    emit("world", {"message": "Hello World!"})


app_logger.info(f"✅ Custom SocketIO Events registriert")
