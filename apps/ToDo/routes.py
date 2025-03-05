from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint
from app.config import Config
from app.decorators import admin_required
from .models import ToDo
from app import db
from datetime import datetime
from pytz import timezone

config = Config()


def get_information(user_id):
    # Anzahl Aufgaben bis heute von dem spezifischem Benutzer
    # aktuelles Datum
    # Aufgaben bis heute
    count_task = ToDo.query.filter_by(user=user_id).count()
    current_date = datetime.now(timezone("Europe/Zurich"))  # Mit Zeitzone
    current_task = ToDo.query.filter_by(user=user_id).all()

    return count_task, current_date, current_task


def create_task(user, data):
    try:
        # Datum-String in datetime-Objekt umwandeln
        task_date_str = data["taskDate"]
        task_date = datetime.strptime(task_date_str, "%Y-%m-%d")

        # Zeitzone hinzufügen
        zurich_tz = timezone("Europe/Zurich")
        task_date = zurich_tz.localize(task_date)

        new_task = ToDo(
            user=user.id,
            task=data["taskTitle"],
            state=0,  # 0 für offen
            to_do_date=task_date,
        )
        db.session.add(new_task)
        db.session.commit()
        return True, None
    except Exception as e:
        app.logger.error(f"Fehler beim Erstellen der Aufgabe: {e}")
        db.session.rollback()
        return False, str(e)


@blueprint.route("/ToDo_index", methods=["GET", "POST"])
def ToDo_index():
    app.logger.info("ToDo page accessed")

    # Hole die Informationen vom Benutzer
    count_task, current_date, current_task = get_information(current_user.id)

    if request.method == "POST":
        data = request.form
        success, error = create_task(current_user, data)
        if not success:
            app.logger.error(f"Fehler beim Erstellen der Aufgabe: {error}")
        else:
            # Nach erfolgreicher Erstellung die Daten aktualisieren
            count_task, current_date, current_task = get_information(current_user.id)

    return render_template(
        "todo.html",
        user=current_user,
        config=config,
        count_task=count_task,
        current_date=current_date,
    )
