from flask import render_template, request
from flask_login import current_user
from app.decorators import admin_required, enabled_required

# # Import aus Parent Package (Template_app_v002/__init__.py)
from ... import blueprint, app_logger, app_config, APP_ROOT


# Import AdminHelper-Klasse
from ..._base.helper_app_function.helper_admin_app import AdminHelper, is_ajax_request


# # Import Socket-Manager
# from app.socketio_manager import get_socketio_manager

# # Import Socket-Funktionen
# from ..socketio_events import get_active_sockets, get_socket_count

# # Import Tasks
# from ..tasks import get_all_tasks

app_logger.info(f"Starte CUSTOM Admin Routes für {app_config.app_name}")
# ========================================
# ADMIN VIEW ROUTES (nur render_template, keine APIs)
# ========================================


@blueprint.route("/admin_custom_setting_01", methods=["GET"])
@admin_required
def admin_custom_setting_01():
    if is_ajax_request():
        return render_template(
            "_custom/admin/Template_app_v002_admin_custom_setting_01.html",
            user=current_user,
            config=app_config,
            app_config=app_config,
        )

    return render_template(
        "Template_app_v002.html",
        user=current_user,
        config=app_config,
        content="admin_custom_setting_01",
        settings="app_info",
        app_config=app_config,
    )


app_logger.info(f"Ende CUSTOM Admin Routes für {app_config.app_name}")
