"""
Keep Alive Log Job
"""

from ... import app_logger, app_config, APP_NAME


def app_keep_alive_log():
    """
    Keep Alive Log - zeigt an dass die App läuft
    """
    try:
        app_logger.info(f"💓 Keep Alive | App: {APP_NAME} v{app_config.app_version}")
        return True

    except Exception as e:
        app_logger.error(f"❌ Fehler in Keep Alive Log: {str(e)}")
        return False
