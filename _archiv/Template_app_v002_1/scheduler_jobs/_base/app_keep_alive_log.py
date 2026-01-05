from .. import app_logger
from ..app_config import AppConfig

app_config = AppConfig()


def app_keep_alive_log():
    """
    Hauptfunktion zur Synchronisation des Dateisystems mit der Datenbank
    """
    app_logger.info(f"Keep Alive Log für die App {app_config.app_name}")
