from . import app_logger
from flask_apscheduler import APScheduler
from .scheduler_jobs.check_file_system import check_file_system
from .app_config import AppConfig
from app import app
import threading

app_logger.info("Starte App-NexusPlayer Tasks")
app_config = AppConfig()

# Globaler Scheduler für die NexusPlayer App
app_scheduler = APScheduler()


def init_scheduler(app):
    """
    Initialisiere den Scheduler für die NexusPlayer App
    :param app: Flask Anwendungskontext
    """
    try:
        # Timer-Konfiguration
        timer_check_file_system = app_config.get_task_interval("check_file_system")

        # Registriere alle Jobs
        app_scheduler.add_job(
            id="check_file_is_in_db",
            func=check_file_system,
            trigger="interval",
            seconds=timer_check_file_system,
        )

        # Starte den Scheduler
        app_scheduler.init_app(app)
        app_scheduler.start()

        app_logger.info("NexusPlayer Scheduler erfolgreich initialisiert")

        # OPTION 1: Sofortige Ausführung im Hauptthread (EMPFOHLEN für kleine Tasks)
        # app_logger.info("Führe initiale Dateisystem-Prüfung aus...")
        # check_file_system()
        # app_logger.info("Initiale Dateisystem-Prüfung abgeschlossen")

        # OPTION 2: Asynchrone Ausführung in separatem Thread (EMPFOHLEN für lange Tasks)
        app_logger.info("Starte initiale Dateisystem-Prüfung im Hintergrund...")
        initial_check_thread = threading.Thread(
            target=run_initial_check, daemon=True, name="InitialFileSystemCheck"
        )
        initial_check_thread.start()

        # OPTION 3: Trigger Job sofort nach Initialisierung
        # app_scheduler.run_job("check_file_is_in_db")

    except Exception as e:
        app_logger.error(f"Fehler bei der Initialisierung des Schedulers: {str(e)}")


def run_initial_check():
    """
    Führt die initiale Dateisystem-Prüfung in einem separaten Thread aus
    Dies verhindert, dass der App-Start blockiert wird
    """
    import time

    # Kleine Verzögerung, damit Flask vollständig hochgefahren ist
    time.sleep(2)

    try:
        with app.app_context():  # Wichtig für DB-Zugriff!
            app_logger.info("Initiale Dateisystem-Prüfung gestartet")
            check_file_system()
            app_logger.info("Initiale Dateisystem-Prüfung erfolgreich abgeschlossen")
    except Exception as e:
        app_logger.error(f"Fehler bei initialer Dateisystem-Prüfung: {str(e)}")


init_scheduler(app)
app_logger.info("Ende App-NexusPlayer Tasks")
