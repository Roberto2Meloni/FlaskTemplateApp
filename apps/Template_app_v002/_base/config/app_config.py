"""
Minimale App Configuration
Liest _base und _custom Config und merged sie
"""

import json
from pathlib import Path
from typing import Any, Dict


class AppConfig:
    """Einfache Config die _base und _custom merged"""

    def __init__(self, app_name: str, app_root: Path):
        """
        Args:
            app_name: Name der App (z.B. "Template_app_v002")
            app_root: Pfad zum App-Root-Verzeichnis
        """
        self.app_name = app_name
        self.app_root = Path(app_root)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Lade Config: Python-Defaults + _custom Überschreibungen"""

        # 1. Python-Defaults (Single Source of Truth)
        config = {
            "app_display_name": self.app_name,
            "app_version": "0.0.0",
            "app_author": "Unknown",
            "app_description": "",
            "blueprint": {
                "url_prefix": f"/{self.app_name}",
                "static_url_path": f"/{self.app_name}_static",
                "template_folder": "templates",
                "static_folder": "static",
            },
            "logger": {"name": f"APP-{self.app_name}", "level": "INFO"},
            "tasks_intervall": {},
            "features": {
                "socketio_enabled": True,
                "scheduler_enabled": True,
                "admin_panel_enabled": True,
            },
        }

        # 2. Lade _custom Config (überschreibt Python-Defaults)
        # Suche in: _custom/config/ oder config/
        custom_config_paths = [
            self.app_root / "_custom" / "config" / "app_config.json",
            self.app_root / "config" / "app_config.json",
        ]

        for custom_config in custom_config_paths:
            if custom_config.exists():
                with open(custom_config, "r", encoding="utf-8") as f:
                    custom_data = json.load(f)
                    # Deep merge für nested dicts
                    for key, value in custom_data.items():
                        if (
                            isinstance(value, dict)
                            and key in config
                            and isinstance(config[key], dict)
                        ):
                            config[key].update(value)
                        else:
                            config[key] = value
                break  # Nur erste gefundene Custom-Config laden

        return config

    # Properties
    @property
    def app_display_name(self) -> str:
        return self.config.get("app_display_name", self.app_name)

    @property
    def app_version(self) -> str:
        return self.config.get("app_version", "0.0.0")

    @property
    def app_author(self) -> str:
        return self.config.get("app_author", "Unknown")

    @property
    def app_description(self) -> str:
        return self.config.get("app_description", "")

    @property
    def blueprint_url_prefix(self) -> str:
        return self.config.get("blueprint", {}).get("url_prefix", f"/{self.app_name}")

    @property
    def blueprint_static_url_path(self) -> str:
        return self.config.get("blueprint", {}).get(
            "static_url_path", f"/{self.app_name}_static"
        )

    @property
    def blueprint_template_folder(self) -> str:
        return self.config.get("blueprint", {}).get("template_folder", "templates")

    @property
    def blueprint_static_folder(self) -> str:
        return self.config.get("blueprint", {}).get("static_folder", "static")

    @property
    def logger_name(self) -> str:
        return self.config.get("logger", {}).get("name", f"APP-{self.app_name}")

    @property
    def logger_level(self) -> str:
        return self.config.get("logger", {}).get("level", "INFO")

    @property
    def socketio_enabled(self) -> bool:
        """Ist SocketIO aktiviert?"""
        return self.config.get("features", {}).get("socketio_enabled", True)

    @property
    def scheduler_enabled(self) -> bool:
        """Ist Scheduler aktiviert?"""
        return self.config.get("features", {}).get("scheduler_enabled", True)

    @property
    def admin_panel_enabled(self) -> bool:
        """Ist Admin-Panel aktiviert?"""
        return self.config.get("features", {}).get("admin_panel_enabled", True)

    @property
    def tasks_intervals(self) -> Dict[str, int]:
        """Alle Task-Intervalle"""
        return self.config.get("tasks_intervall", {})

    def get_task_interval(self, task_name: str, default: int = 5) -> int:
        """
        Hole Intervall für spezifischen Task

        Args:
            task_name: Name des Tasks (z.B. "app_keep_alive_log")
            default: Standard-Intervall in Minuten

        Returns:
            Intervall in Minuten
        """
        return self.tasks_intervals.get(task_name, default)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Hole Config-Wert mit Punktnotation
        Beispiel: config.get("blueprint.url_prefix")
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default
