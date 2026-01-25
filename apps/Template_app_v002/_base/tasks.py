"""
Template_app_v002 Tasks & Scheduler
"""

import threading
from .. import app_logger, app_config, APP_NAME  # ✅ Aus Haupt-__init__.py
from flask_apscheduler import APScheduler
from app.scheduler_manager import register_scheduler
from .scheduler_jobs.app_keep_alive_log import app_keep_alive_log

app_logger.info(f"Starte App-{APP_NAME} Tasks")

# Lokaler App-Scheduler
app_scheduler = APScheduler()


def init_scheduler(flask_app):
    """
    Initialisiert den Scheduler für diese App

    Args:
        flask_app: Flask application instance
    """
    try:
        # Definition der Timer
        timer_app_keep_alive_log = app_config.get_task_interval("app_keep_alive_log")

        app_scheduler.add_job(
            id=f"{APP_NAME}_app_keep_alive_log",
            func=app_keep_alive_log,
            trigger="interval",
            minutes=timer_app_keep_alive_log,
        )

        app_scheduler.init_app(flask_app)
        app_scheduler.start()

        # Registriere Scheduler im globalen Manager
        register_scheduler(APP_NAME, app_scheduler)

        app_logger.info(f"✅ Scheduler für {APP_NAME} initialisiert")

        # Initiale Ausführung in separatem Thread
        thread_app_keep_alive_log = threading.Thread(
            target=run_initial_app_keep_alive_log,  # ✅ Korrigiert
            args=(flask_app,),  # ✅ App-Kontext übergeben
            daemon=True,
            name=f"Init_{APP_NAME}_keep_alive_log",
        )
        thread_app_keep_alive_log.start()

    except Exception as e:
        app_logger.error(f"Fehler beim Initialisieren von {APP_NAME} Tasks: {e}")


def run_initial_app_keep_alive_log(flask_app):
    """
    Führt die initiale Keep Alive Log aus

    Args:
        flask_app: Flask application instance für app_context
    """
    import time

    time.sleep(2)

    try:
        with flask_app.app_context():
            app_logger.info(f"Initiale Keep Alive Log für {APP_NAME} gestartet")
            app_keep_alive_log()  # ✅ Korrigiert - war rekursiv!
            app_logger.info("Initiale Keep Alive Log erfolgreich abgeschlossen")
    except Exception as e:
        app_logger.error(f"Fehler bei initialer Keep Alive Log: {str(e)}")


def get_all_tasks():
    """
    Holt alle registrierten Tasks aus dem App-Scheduler

    Returns:
        list: Liste mit Task-Informationen
    """
    try:
        tasks = []
        jobs = app_scheduler.get_jobs()

        for job in jobs:
            # Filtere nur Jobs dieser App
            if job.id.startswith(APP_NAME):
                # Prüfe ob Job pausiert ist
                is_paused = False
                if hasattr(job, "next_run_time") and job.next_run_time is None:
                    is_paused = True

                task_info = {
                    "id": job.id,
                    "name": job.name if job.name else job.id,
                    "next_run": (
                        job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
                        if job.next_run_time
                        else "Pausiert" if is_paused else "Nicht geplant"
                    ),
                    "trigger": str(job.trigger),
                    "func": (
                        job.func.__name__
                        if hasattr(job.func, "__name__")
                        else "Unbekannt"
                    ),
                    "active": not is_paused,
                }
                tasks.append(task_info)

        app_logger.debug(f"Gefundene Tasks: {len(tasks)}")
        return tasks

    except Exception as e:
        app_logger.error(f"Fehler beim Laden der Tasks: {e}")
        return []


# ❌ ENTFERNEN - wird von init_app() aufgerufen!
# init_scheduler(app)
# app_logger.info(f"Ende App-{app_config.app_name} Tasks")

app_logger.info(f"Ende App-{APP_NAME} Tasks Modul geladen")
