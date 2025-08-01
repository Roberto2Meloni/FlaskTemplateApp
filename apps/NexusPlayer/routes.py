from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint
from app.config import Config
from app.decorators import admin_required, enabled_required
from app import db

# for Debuging
from icecream import ic

# from .models import xx
# from app.admin.models import User@
# from app.helper_functions.helper_db_file import check_if_user_has_admin_rights

config = Config()

print("NexusPlayer Version 0.0.0")


@blueprint.route("/NexusPlayer_index", methods=["GET"])
@enabled_required
def NexusPlayer_index():
    return render_template("NexusPlayer.html", user=current_user, config=config)


@blueprint.route("/test_flex", methods=["GET"])
@admin_required
def test_flex():
    return render_template("test_flex.html", user=current_user, config=config)
