import threading
from app.scheduler_manager import register_scheduler
from . import app_logger
from flask_apscheduler import APScheduler
from .scheduler_jobs.check_file_system import check_file_system
from .scheduler_jobs.check_playlist_system import check_playlist_system
from .app_config import AppConfig
from app import app


app_scheduler = APScheduler()
app_config = AppConfig()
app_logger.info(f"Starte App-{app_config.app_name} Tasks")


def init_scheduler(app):
    """
    Initialisiere den Scheduler für die NexusPlayer App
    :param app: Flask Anwendungskontext
    """
    try:
        # Die Timer sauber als variabel
        timer_check_file_system = app_config.get_task_interval("check_file_system")
        timer_check_playlist_system = app_config.get_task_interval(
            "check_playlist_system"
        )

        # Registriere File-System Job
        app_scheduler.add_job(
            id=f"{app_config.app_name}_check_file_system",
            func=check_file_system,
            trigger="interval",
            minutes=timer_check_file_system,
        )

        # Registriere Playlist-System Job
        app_scheduler.add_job(
            id=f"{app_config.app_name}_check_playlist_system",
            func=check_playlist_system,  # ← KORRIGIERT: war check_file_system!
            trigger="interval",
            minutes=timer_check_playlist_system,
        )

        # Starte den Scheduler
        app_scheduler.init_app(app)
        app_scheduler.start()

        register_scheduler(app_config.app_name, app_scheduler)

        app_logger.info(
            f"{app_config.app_name} Scheduler erfolgreich initialisiert "
            f"({len(app_scheduler.get_jobs())} Jobs)"
        )

        # File System Check
        file_check_thread = threading.Thread(
            target=run_initial_file_check, daemon=True, name="InitialFileSystemCheck"
        )
        file_check_thread.start()

        # Playlist Check
        playlist_check_thread = threading.Thread(
            target=run_initial_playlist_check, daemon=True, name="InitialPlaylistCheck"
        )
        playlist_check_thread.start()

    except Exception as e:
        app_logger.error(f"Fehler bei der Initialisierung des Schedulers: {str(e)}")


def run_initial_file_check():
    """Führt die initiale Dateisystem-Prüfung aus"""
    import time

    time.sleep(2)

    try:
        with app.app_context():
            app_logger.info("Initiale Dateisystem-Prüfung gestartet")
            check_file_system()
            app_logger.info("Initiale Dateisystem-Prüfung erfolgreich abgeschlossen")
    except Exception as e:
        app_logger.error(f"Fehler bei initialer Dateisystem-Prüfung: {str(e)}")


def run_initial_playlist_check():
    """Führt die initiale Playlist-Prüfung aus"""
    import time

    time.sleep(4)  # Etwas später als File-Check

    try:
        with app.app_context():
            app_logger.info("Initiale Playlist-Prüfung gestartet")
            check_playlist_system()
            app_logger.info("Initiale Playlist-Prüfung erfolgreich abgeschlossen")
    except Exception as e:
        app_logger.error(f"Fehler bei initialer Playlist-Prüfung: {str(e)}")


# Initialisiere Scheduler
init_scheduler(app)
app_logger.info(f"Ende App-{app_config.app_name} Tasks")
