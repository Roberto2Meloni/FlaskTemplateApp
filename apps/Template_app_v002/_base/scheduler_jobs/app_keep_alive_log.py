from ... import app_logger, app_config  # ✅ Beide aus Haupt-__init__.py


def app_keep_alive_log():
    """
    Hauptfunktion zur Synchronisation des Dateisystems mit der Datenbank
    """
    app_logger.info(f"Keep Alive Log für die App {app_config.app_name}")
