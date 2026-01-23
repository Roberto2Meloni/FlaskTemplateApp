"""
Base API Routes
"""

from flask import jsonify
from flask_login import current_user
from app.decorators import admin_required, enabled_required

# Import aus Parent Package (Template_app_v002)
from .. import blueprint, app_logger, app_config

app_logger.info(f"Starte API Routes für {app_config.app_name}")

# ============================================
# API ROUTES
# ============================================


@blueprint.route("/api/status", methods=["GET"])
@enabled_required
def api_status():
    """Status-Endpoint"""
    return jsonify(
        {
            "status": "ok",
            "app_name": app_config.app_name,
            "version": app_config.app_version,
        }
    )


@blueprint.route("/api/info", methods=["GET"])
@enabled_required
def api_info():
    """App-Info Endpoint"""
    return jsonify(
        {
            "name": app_config.app_name,
            "display_name": app_config.app_display_name,
            "version": app_config.app_version,
            "author": app_config.app_author,
            "socketio": app_config.socketio_enabled,
            "scheduler": app_config.scheduler_enabled,
        }
    )


# Weitere API Routes hier...

app_logger.info(f"Ende API Routes für {app_config.app_name}")
