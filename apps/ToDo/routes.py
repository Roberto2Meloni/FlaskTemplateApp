from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint
from app.config import Config
from app.decorators import admin_required
from .models import ToDo
from app import db
from datetime import datetime

config = Config()


def get_information(user_id):
    # Anzahl Aufgaben bis heute von dem spezifischem Benutzer
    # aktuelles Datum
    # Aufgaben bis heute
    count_task = ToDo.query.filter_by(user=user_id).count()
    current_date = datetime.now()  # Hier das reine datetime-Objekt
    current_task = ToDo.query.filter_by(user=user_id).all()

    return count_task, current_date, current_task


def create_task(user, data):
    try:
        new_task = ToDo(
            user=user.username, task=data["taskTitle"], to_do_date=data["taskDate"]
        )
        db.session.add(new_task)
        db.session.commit()
    except Exception as e:
        print(f"Fehler beim Erstellen: {e}")
        db.session.rollback()
        raise


@blueprint.route("/ToDo_index", methods=["GET", "POST"])
def ToDo_index():
    app.logger.info("ToDo page accessed")

    # Hole die Informationen vom Benutzer
    count_task, current_date, current_task = get_information(current_user.id)

    if request.method == "POST":
        data = request.form
        create_task(current_user, data)

    print("---LOG---")
    print(f"Anzahl Aufgaben: {count_task}")
    print(f"Aktuelles Datum: {current_date}")
    print(f"Aktuelle Aufgaben: {current_task}")
    print("---LOG---")

    return render_template(
        "todo.html",
        user=current_user,
        config=config,
        count_task=count_task,
        current_date=current_date,
        current_task=current_task,
    )
