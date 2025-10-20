from . import app_logger
from flask_apscheduler import APScheduler
from app.scheduler_manager import register_scheduler
from .app_config import AppConfig
from .scheduler_jobs.app_test_hello_world import app_test_hello_world
from app import app

app_scheduler = APScheduler()
app_config = AppConfig()
app_logger.info("Starte App-Template_app_v001 Tasks")


def init_scheduler(app):
    try:
        # Definition der Timer
        timer_app_test_hello_wold = app_config.get_task_interval("app_test_hello_wold")

        app_scheduler.add_job(
            id=f"{app_config.app_name}_app_test_hello_world",
            func=app_test_hello_world,
            trigger="interval",
            seconds=timer_app_test_hello_wold,
        )  # Deine Jobs

        app_scheduler.init_app(app)
        app_scheduler.start()

        # Diese 2 Zeilen hinzufügen:
        register_scheduler(app_config.app_name, app_scheduler)
        print("Scherudler für app_hello wordl integirert")
    except Exception as e:
        app_logger.error(f"Fehler beim Initialisieren der App-NeueApp Tasks: {e}")


init_scheduler(app)
app_logger.info("Ende App-Template_app_v001 Tasks")
