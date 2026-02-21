import os
import json
from typing import Dict, Any


class AppConfig:
    """
    Konfigurationsklasse für die App
    Liest Konfigurationen aus der app_config.json mit Default-Werten
    """

    _config_data = None
    _app_name = "Template_app_v001"

    def __init__(self):
        """
        Initialisiere die Konfiguration
        Lädt Konfiguration und wendet Standardwerte an
        """
        if AppConfig._config_data is None:
            self._load_config()
        self._save_config()

    def _load_config(self):
        """
        Lade Konfiguration aus der JSON-Datei
        """
        try:
            root_path = os.getcwd()
            app_path = os.path.join(
                root_path, "app", "imported_apps", "develop_release", self._app_name
            )
            config_path = os.path.join(app_path, "app_config.json")

            with open(config_path, "r", encoding="utf-8") as file:
                AppConfig._config_data = json.load(file)
        except FileNotFoundError:
            print(f"Warnung: Konfigurationsdatei nicht gefunden: {config_path}")
            AppConfig._config_data = {}
        except json.JSONDecodeError:
            print(f"Fehler: Ungültiges JSON in {config_path}")
            AppConfig._config_data = {}

    def _save_config(self):
        """
        Speichere die Konfiguration in der JSON-Datei
        """
        try:
            root_path = os.getcwd()
            app_path = os.path.join(
                root_path, "app", "imported_apps", "develop_release", self._app_name
            )
            config_path = os.path.join(app_path, "app_config.json")

            with open(config_path, "w", encoding="utf-8") as file:
                json.dump(AppConfig._config_data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Fehler beim Speichern der Konfiguration: {e}")

    @classmethod
    def refresh(cls):
        """
        Lade die Konfiguration neu
        """
        cls._config_data = None
        instance = cls()
        instance._load_config()

    def to_dict(self) -> Dict[str, Any]:
        """
        Konvertiere die Konfiguration zu einem Dictionary für Template-Verwendung
        :return: Dictionary mit allen Konfigurationswerten
        """
        return AppConfig._config_data.copy() if AppConfig._config_data else {}

    def update_config(self, updates: Dict[str, Any], skip_app_name: bool = True):
        """
        Aktualisiere mehrere Konfigurationswerte auf einmal
        :param updates: Dictionary mit zu aktualisierenden Werten
        :param skip_app_name: Wenn True, wird app_name nicht überschrieben
        """
        if AppConfig._config_data is None:
            self._load_config()

        for key, value in updates.items():
            if skip_app_name and key == "app_name":
                continue
            AppConfig._config_data[key] = value

        self._save_config()

    def set(self, key: str, value: Any):
        """
        Setze einen Konfigurationswert und speichere
        :param key: Schlüssel in der Konfiguration
        :param value: Neuer Wert
        """
        if AppConfig._config_data is None:
            self._load_config()

        # Verhindere Änderung des app_name
        if key == "app_name":
            print("Warnung: app_name kann nicht geändert werden")
            return

        AppConfig._config_data[key] = value
        self._save_config()

    # Eigenschaften für häufig verwendete Konfigurationswerte
    @property
    def app_name(self):
        return AppConfig._config_data.get("app_name", self._app_name)

    @property
    def tasks_intervals(self):
        return AppConfig._config_data.get("tasks_intervall", {})

    def get(self, key: str, default: Any = None) -> Any:
        """
        Hole einen Konfigurationswert
        :param key: Schlüssel in der Konfiguration (mit Punktnotation möglich)
        :param default: Standardwert, wenn Schlüssel nicht existiert
        :return: Wert des Schlüssels oder Standardwert
        """
        if AppConfig._config_data is None:
            return default

        keys = key.split(".")
        value = AppConfig._config_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value if value != default else default

    def get_tasks_intervals(self) -> Dict[str, int]:
        """
        Hole alle Task-Intervalle
        :return: Dictionary mit Task-Namen und ihren Intervallen
        """
        return self.get("tasks_intervall", {})

    def get_task_interval(self, task_name: str, default: int = 5) -> int:
        """
        Hole das Intervall für einen spezifischen Task
        :param task_name: Name des Tasks
        :param default: Standardintervall (Standard: 5 Minuten)
        :return: Intervall in Minuten
        """
        intervals = self.get_tasks_intervals()
        return intervals.get(task_name, default)

    def __repr__(self):
        """
        Gib eine formatierte String-Repräsentation der Konfiguration zurück
        """
        return json.dumps(AppConfig._config_data, indent=2)
