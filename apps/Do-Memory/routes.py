from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint
from app.config import Config
from app.decorators import admin_required
from .models import CliCommandHistory
from app import db
import subprocess
import uuid
import threading
import queue
import sys

config = Config()

# Dictionary to store running commands
running_commands = {}

print("Do-Memory Version 0.0.0")


@blueprint.route("/do-memory_index", methods=["GET"])
@admin_required
def cli_index():
    app.logger.info("CLI page accessed")
    return render_template("cli.html", user=current_user, config=config)
