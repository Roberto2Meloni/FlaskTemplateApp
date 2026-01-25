import threading
from . import app_logger
from flask_apscheduler import APScheduler
from app.scheduler_manager import register_scheduler
from .app_config import AppConfig
from .scheduler_jobs.app_keep_alive_log import app_keep_alive_log
from app import app

app_scheduler = APScheduler()
app_config = AppConfig()
app_logger.info(f"Starte App-{app_config.app_name} Tasks")


def init_scheduler(app):
    try:
        # Definition der Timer
        timer_app_keep_alive_log = app_config.get_task_interval("app_keep_alive_log")

        app_scheduler.add_job(
            id=f"{app_config.app_name}_app_keep_alive_log",
            func=app_keep_alive_log,
            trigger="interval",
            minutes=timer_app_keep_alive_log,
        )  # Deine Jobs

        app_scheduler.init_app(app)
        app_scheduler.start()

        # Diese 2 Zeilen hinzufügen:
        register_scheduler(app_config.app_name, app_scheduler)

        # Hier werden die Jobs initial in einem separaten Thread ausgeführt
        # Keep Alive Log
        thread_app_keep_alive_log = threading.Thread(
            target=app_keep_alive_log, daemon=True, name="Init_app_keep_alive_log"
        )
        thread_app_keep_alive_log.start()

    except Exception as e:
        app_logger.error(f"Fehler beim Initialisieren der App-NeueApp Tasks: {e}")


def run_initial_app_keep_alive_log():
    """Führt die initiale Dateisystem-Prüfung aus"""
    import time

    time.sleep(2)

    try:
        with app.app_context():
            app_logger.info("Initiale Keep Alive Log für die App gestartet")
            run_initial_app_keep_alive_log()
            app_logger.info("Initiale Keep Alive Log erfolgreich abgeschlossen")
    except Exception as e:
        app_logger.error(f"Fehler bei initialer Keep Alive Log für die App: {str(e)}")


def get_all_tasks():
    """
    Holt alle registrierten Tasks aus dem App-Scheduler
    """
    try:
        from .tasks import app_scheduler

        tasks = []
        jobs = app_scheduler.get_jobs()

        for job in jobs:
            # Filtere nur Jobs dieser App
            if job.id.startswith(app_config.app_name):
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


init_scheduler(app)
app_logger.info(f"Ende App-{app_config.app_name} Tasks")
