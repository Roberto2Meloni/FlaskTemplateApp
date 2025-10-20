from .. import app_logger
from .. import app_config


def app_test_hello_world():
    """
    Hauptfunktion zur Synchronisation des Dateisystems mit der Datenbank
    """
    app_logger.info("Start Test Hello World für App")
    try:
        print(f"Hello World von {app_config.app_name}")
        app_logger.info("Ende check_file_system")
    except Exception as e:
        app_logger.critical(f"Kritischer Fehler in check_file_system: {str(e)}")
