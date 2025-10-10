from . import blueprint, app_logger
from app.decorators import admin_required, enabled_required
from flask import render_template
from flask_login import current_user
from app.config import Config

config = Config()
app_logger.info("Starte App-Template_app_v001 Content")


@blueprint.route("/content/dashboard", methods=["GET"])
@enabled_required
def content_dashboard():
    return render_template(
        "content/Template_app_v001_dashboard.html", user=current_user, config=config
    )


@blueprint.route("/content/Page_01", methods=["GET"])
@enabled_required
def content_page_01():
    return render_template(
        "content/Template_app_v001_page_01.html", user=current_user, config=config
    )


@blueprint.route("/content/Page_02", methods=["GET"])
@enabled_required
def content_page_02():
    return render_template(
        "content/Template_app_v001_page_02.html", user=current_user, config=config
    )


@blueprint.route("/content/Page_03", methods=["GET"])
@enabled_required
def content_page_03():
    return render_template(
        "content/Template_app_v001_page_03.html", user=current_user, config=config
    )


@blueprint.route("/content/app_settings", methods=["GET"])
@admin_required
def content_app_settings():
    return render_template(
        "content/Template_app_v001_app_settings.html", user=current_user, config=config
    )


app_logger.info("Ende App-Template_app_v001 Content")
