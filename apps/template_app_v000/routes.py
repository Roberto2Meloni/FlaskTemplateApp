from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint
from app.config import Config
from app.decorators import admin_required
from .models import CliCommandHistory
from app import db

config = Config()

print("Template_app_v000 Version 0.0.0")


@blueprint.route("/Template_app_v000_index", methods=["GET"])
@admin_required
def Template_app_v000_index():
    return render_template(
        "Template_app_v000_index.html", user=current_user, config=config
    )
