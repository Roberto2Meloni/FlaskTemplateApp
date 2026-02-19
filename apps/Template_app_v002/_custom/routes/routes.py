"""
Content Routes für Template_app_v002
Hier kommen die Haupt-Seiten und User-facing Routes
"""

from flask import render_template, request
from flask_login import current_user
from ... import blueprint, app_logger, app_config, APP_NAME
from app.decorators import enabled_required
from app.config import Config

config = Config()

app_logger.info(f"Starte Content Routes für {APP_NAME}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def is_ajax_request():
    """Prüft ob der Request von fetch/JavaScript kommt"""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


# ============================================================================
# INDEX / HAUPTSEITE
# ============================================================================


@blueprint.route(f"/{APP_NAME}_index")
@blueprint.route("/")
@enabled_required
def Template_app_v002_index():
    """Hauptseite der App"""
    app_logger.info(f"{APP_NAME} Index-Seite aufgerufen")

    return render_template(
        "Template_app_v002.html",
        user=current_user,
        config=config,
        content="dashboard",  # ✅ Lädt Dashboard-Content
        app_config=app_config,
    )


# ============================================================================
# CONTENT SEITEN
# ============================================================================


@blueprint.route("/dashboard", methods=["GET"])
@enabled_required
def dashboard():
    """Dashboard"""
    app_logger.info(f"{APP_NAME} Dashboard aufgerufen")

    # Bei AJAX: Nur Content
    if is_ajax_request():
        return render_template(
            "_custom/content/Template_app_v002_dashboard.html",
            user=current_user,
            config=config,
            app_config=app_config,
        )

    # Normal: Komplette Seite mit Layout
    return render_template(
        "_base/Template_app_v002.html",  # ✅ Haupt-Template
        user=current_user,
        config=config,
        content="dashboard",  # ✅ content-Variable
        app_config=app_config,
    )


@blueprint.route("/page_01", methods=["GET"])
@enabled_required
def page_01():
    """Seite 1"""
    app_logger.info(f"{APP_NAME} Page 01 aufgerufen")

    if is_ajax_request():
        return render_template(
            "_custom/content/Template_app_v002_page_01.html",
            user=current_user,
            config=config,
            app_config=app_config,
        )

    return render_template(
        "_base/Template_app_v002.html",
        user=current_user,
        config=config,
        content="page_01",  # ✅ Lädt page_01
        app_config=app_config,
    )


@blueprint.route("/page_02", methods=["GET"])
@enabled_required
def page_02():
    """Seite 2"""
    app_logger.info(f"{APP_NAME} Page 02 aufgerufen")

    if is_ajax_request():
        return render_template(
            "_custom/content/Template_app_v002_page_02.html",
            user=current_user,
            config=config,
            app_config=app_config,
        )

    return render_template(
        "_base/Template_app_v002.html",
        user=current_user,
        config=config,
        content="page_02",  # ✅
        app_config=app_config,
    )


@blueprint.route("/page_03", methods=["GET"])
@enabled_required
def page_03():
    """Seite 3"""
    app_logger.info(f"{APP_NAME} Page 03 aufgerufen")

    if is_ajax_request():
        return render_template(
            "_custom/content/Template_app_v003_page_03.html",
            user=current_user,
            config=config,
            app_config=app_config,
        )

    return render_template(
        "_base/Template_app_v002.html",
        user=current_user,
        config=config,
        content="page_03",  # ✅
        app_config=app_config,
    )


app_logger.info(f"Ende Content Routes für {APP_NAME}")
