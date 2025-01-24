from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint
from app.config import Config
from app.decorators import admin_required
from .models import CliCommandHistory
from app import db


config = Config()
print("ToDo app 0.0.1")


@blueprint.route("/todo_index", methods=["GET"])
@admin_required
def todo_index():
    app.logger.info("ToDo page accessed")
    return render_template("todo.html", user=current_user, config=config)
