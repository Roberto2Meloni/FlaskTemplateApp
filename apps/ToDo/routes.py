from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint
from app.config import Config
from app.decorators import admin_required
from .models import ToDo
from app import db


config = Config()


@blueprint.route("/ToDo_index", methods=["GET"])
@admin_required
def ToDo_index():
    app.logger.info("ToDo page accessed")
    my_todos = ToDo.query.filter_by(user=current_user.id).all()
    return render_template(
        "todo.html", user=current_user, config=config, my_todos=my_todos
    )
