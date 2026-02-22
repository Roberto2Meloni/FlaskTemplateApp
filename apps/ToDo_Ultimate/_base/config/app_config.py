"""
Minimale App Configuration
Liest _base und _custom Config und merged sie

Neues Attribut hinzufügen:
  1. In _get_defaults() eintragen
  2. Property definieren
  → wird automatisch ins JSON geschrieben beim nächsten Start

Readonly-Felder (können nicht vom JSON überschrieben werden):
  → In _READONLY_FIELDS eintragen
  → admin_app_version: kommt immer aus _BASE_VERSION (Update-Script)
  → app_version: NICHT readonly, wird vom Update-Script im JSON erhöht
"""

import json
from pathlib import Path
from typing import Any, Dict


class AppConfig:
    """Config die _base Defaults mit _custom JSON merged und synct"""

    # ========================================
    # BASE VERSION — wird vom Update-Script gesetzt
    # Zeigt welche _base Version diese App hat
    # ========================================
    _BASE_VERSION = "0.0.1"

    # ========================================
    # READONLY FIELDS
    # Nur admin_app_version ist readonly.
    # app_version ist NICHT readonly — wird vom Update-Script im JSON erhöht.
    # ========================================
    _READONLY_FIELDS = {
        "admin_app_version": _BASE_VERSION,
    }

    # ========================================
    # DEFAULTS
    # ========================================

    def _get_defaults(self) -> Dict[str, Any]:
        """Python-Defaults — neue Felder hier eintragen"""
        return {
            "app_display_name": self.app_name,
            "app_version": "0.0.0",  # ← vom Update-Script erhöht, NICHT readonly
            "admin_app_version": self._BASE_VERSION,  # ← readonly, immer aus _BASE_VERSION
            "app_author": "Unknown",
            "app_description": "",
            "blueprint": {
                "url_prefix": f"/{self.app_name}",
                "static_url_path": f"/{self.app_name}_static",
                "template_folder": "templates",
                "static_folder": "static",
            },
            "logger": {
                "name": f"APP-{self.app_name}",
                "level": "INFO",
            },
            "tasks_intervall": {},
            "features": {
                "socketio_enabled": True,
                "scheduler_enabled": True,
                "admin_panel_enabled": True,
            },
        }

    def __init__(self, app_name: str, app_root: Path):
        self.app_name = app_name
        self.app_root = Path(app_root)
        self.config = self._load_config()

    # ========================================
    # LADEN & MERGEN
    # ========================================

    def _load_config(self) -> Dict[str, Any]:
        config = self._get_defaults()
        custom_config_path = self._find_custom_config()

        if custom_config_path and custom_config_path.exists():
            with open(custom_config_path, "r", encoding="utf-8") as f:
                custom_data = json.load(f)

            self._deep_merge(config, custom_data)
            config = self._apply_readonly_fields(config)

            needs_sync = self._find_missing_keys(custom_data, self._get_defaults())
            needs_version_update = self._check_readonly_changed(custom_data)

            if needs_sync or needs_version_update:
                if needs_sync:
                    print(f"[AppConfig] Neue Felder ins JSON geschrieben: {needs_sync}")
                if needs_version_update:
                    print(
                        f"[AppConfig] Readonly-Felder aktualisiert: {needs_version_update}"
                    )
                self._write_config(custom_config_path, config)
        else:
            config = self._apply_readonly_fields(config)
            path = self._get_default_custom_config_path()
            self._write_config(path, config)
            print(f"[AppConfig] Neue Config erstellt: {path}")

        return config

    def _apply_readonly_fields(self, config: dict) -> dict:
        for key, value in self._READONLY_FIELDS.items():
            config[key] = value
        return config

    def _check_readonly_changed(self, existing_json: dict) -> list:
        changed = []
        for key, value in self._READONLY_FIELDS.items():
            if existing_json.get(key) != value:
                changed.append(f"{key}: {existing_json.get(key)} → {value}")
        return changed

    def _find_custom_config(self) -> Path | None:
        candidates = [
            self.app_root / "_custom" / "config" / "app_config.json",
            self.app_root / "config" / "app_config.json",
        ]
        for path in candidates:
            if path.exists():
                return path
        return None

    def _get_default_custom_config_path(self) -> Path:
        return self.app_root / "_custom" / "config" / "app_config.json"

    def _deep_merge(self, base: dict, override: dict) -> None:
        for key, value in override.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _find_missing_keys(
        self, existing: dict, defaults: dict, prefix: str = ""
    ) -> list:
        missing = []
        for key, value in defaults.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if key not in existing:
                missing.append(full_key)
            elif isinstance(value, dict) and isinstance(existing.get(key), dict):
                missing.extend(self._find_missing_keys(existing[key], value, full_key))
        return missing

    # ========================================
    # SPEICHERN
    # ========================================

    def _write_config(self, path: Path, config: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _save_config(self) -> None:
        self.config = self._apply_readonly_fields(self.config)
        path = self._find_custom_config() or self._get_default_custom_config_path()
        try:
            self._write_config(path, self.config)
            print(f"✓ Config gespeichert: {path}")
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Config: {e}")
            raise

    # ========================================
    # PROPERTIES
    # ========================================

    @property
    def app_display_name(self) -> str:
        return self.config.get("app_display_name", self.app_name)

    @property
    def app_version(self) -> str:
        return self.config.get("app_version", "0.0.0")

    @property
    def admin_app_version(self) -> str:
        """Readonly — kommt immer aus _BASE_VERSION"""
        return self._BASE_VERSION

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
        return self.config.get("features", {}).get("socketio_enabled", True)

    @property
    def scheduler_enabled(self) -> bool:
        return self.config.get("features", {}).get("scheduler_enabled", True)

    @property
    def admin_panel_enabled(self) -> bool:
        return self.config.get("features", {}).get("admin_panel_enabled", True)

    @property
    def tasks_intervals(self) -> Dict[str, int]:
        return self.config.get("tasks_intervall", {})

    # ========================================
    # PUBLIC API
    # ========================================

    def get_task_interval(self, task_name: str, default: int = 5) -> int:
        return self.tasks_intervals.get(task_name, default)

    def get(self, key: str, default: Any = None) -> Any:
        """Hole Config-Wert mit Punktnotation: config.get('features.socketio_enabled')"""
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

    def set(self, key: str, value: Any) -> None:
        """
        Setze Config-Wert mit Punktnotation und speichere.
        Readonly-Felder können nicht gesetzt werden.
        """
        if key in self._READONLY_FIELDS:
            raise ValueError(
                f"'{key}' ist readonly und kann nicht über set() geändert werden.\n"
                f"Ändere _BASE_VERSION direkt in app_config.py."
            )
        keys = key.split(".")
        current = self.config
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
        self._save_config()

    def reload(self) -> None:
        """Lade Config neu"""
        self.config = self._load_config()
