"""
ToDo_Ultimate Base Tasks & Scheduler
"""

import threading
from .. import app_logger, app_config, APP_NAME
from flask_apscheduler import APScheduler
from app.scheduler_manager import register_scheduler
from .scheduler_jobs.app_keep_alive_log import app_keep_alive_log
from app import app

app_logger.info(f"📦 Lade Base Tasks für {APP_NAME}")

# Lokaler App-Scheduler für Base Tasks
app_scheduler = APScheduler()


def init_scheduler(flask_app):
    """
    Initialisiert den Base-Scheduler für diese App

    Args:
        flask_app: Flask application instance
    """
    try:
        app_logger.info(f"🔧 Initialisiere Base-Scheduler für {APP_NAME}...")

        # Definition der Timer
        timer_app_keep_alive_log = app_config.get_task_interval("app_keep_alive_log")

        # Task hinzufügen
        app_scheduler.add_job(
            id=f"{APP_NAME}_app_keep_alive_log",
            func=app_keep_alive_log,
            trigger="interval",
            minutes=timer_app_keep_alive_log,
            name="Keep Alive Log",
        )

        app_scheduler.init_app(flask_app)
        app_scheduler.start()

        # Registriere Scheduler im globalen Manager
        register_scheduler(APP_NAME, app_scheduler)

        app_logger.info(
            f"✅ Base-Scheduler: '{APP_NAME}_app_keep_alive_log' ({timer_app_keep_alive_log}min)"
        )

        # Initiale Ausführung in separatem Thread
        thread_app_keep_alive_log = threading.Thread(
            target=run_initial_app_keep_alive_log,
            args=(flask_app,),
            daemon=True,
            name=f"Init_{APP_NAME}_keep_alive",
        )
        thread_app_keep_alive_log.start()

    except Exception as e:
        app_logger.error(
            f"❌ Fehler beim Initialisieren von {APP_NAME} Base Tasks: {e}"
        )
        import traceback

        app_logger.error(traceback.format_exc())


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
            app_logger.info(f"🚀 Initiale Keep Alive Log für {APP_NAME}")
            app_keep_alive_log()
    except Exception as e:
        app_logger.error(f"❌ Fehler bei initialer Keep Alive Log: {str(e)}")


def get_all_tasks():
    """
    Holt alle registrierten Tasks aus dem Base-Scheduler

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

        app_logger.debug(f"Base Tasks: {len(tasks)} gefunden")
        return tasks

    except Exception as e:
        app_logger.error(f"❌ Fehler beim Laden der Base Tasks: {e}")
        return []


# ❌ NICHT HIER AUFRUFEN - wird von init_app() aufgerufen!
# init_scheduler(app)

app_logger.info(f"✓ Base Tasks Modul geladen")
