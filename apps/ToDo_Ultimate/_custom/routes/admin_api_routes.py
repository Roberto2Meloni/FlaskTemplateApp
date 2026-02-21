from flask import jsonify, request
from flask_login import current_user
from flask_socketio import disconnect as socketio_disconnect
from app.decorators import admin_required


# Import aus Parent Package (ToDo_Ultimate)
from ... import blueprint, app_logger, app_config, APP_ROOT

# Import Helper (nur AdminHelper-Klasse und convert_value!)
from ..helper_app_function.helper_admin_app import AdminHelper, convert_value

# Import Socket-Management aus socketio_events
from ..socketio_events import active_sockets, remove_socket_connection

app_logger.info(f"Starte CUSTOM Admin API Routes für {app_config.app_name}")

# ========================================
# Dies sind die Custom Admin-API-Routes
# ========================================

app_logger.info(f"Ende CUSTOM Admin API Routes für {app_config.app_name}")
