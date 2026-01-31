"""
Helper Functions für Admin-Bereich
Dynamisch - funktioniert mit jedem App-Namen
"""

import re
import os
from flask import request
from pathlib import Path


class AdminHelper:
    """Helper-Klasse für Admin-Funktionen"""

    def __init__(self, app_config, app_root: Path):
        """
        Args:
            app_config: AppConfig-Instanz
            app_root: Pfad zum App-Root
        """
        self.app_config = app_config
        self.app_root = Path(app_root)

        # Pfade
        self.root_path = Path.cwd()
        self.log_path = self.root_path / "log"
        self.log_file = self.log_path / "server_log.log"
        self.readme_file = self.app_root / "README.md"

    def get_app_logs(self, limit=500, level_filter=None, search_term=None):
        """
        Liest App-Logs effizient - nur die letzten N Zeilen

        Args:
            limit (int): Anzahl der Log-Zeilen die zurückgegeben werden sollen
            level_filter (str): Filter nach Log-Level (INFO, ERROR, WARNING, DEBUG)
            search_term (str): Suchbegriff zum Filtern

        Returns:
            dict: Dictionary mit Log-Informationen
        """
        # Dynamischer Filter basierend auf app_config
        pre_defined_log_filter = self.app_config.logger_name
        additional_filter = r"\[ ?Reboot FLASK ?\]"

        result = {
            "logs": [],
            "total_lines": 0,
            "filtered_lines": 0,
            "file_size_mb": 0,
            "has_more": False,
        }

        try:
            # Hole Dateigröße
            file_size = self.log_file.stat().st_size
            result["file_size_mb"] = round(file_size / (1024 * 1024), 2)

            # Effiziente Rückwärts-Lesung
            if file_size > 10 * 1024 * 1024:  # > 10MB
                read_size = 2 * 1024 * 1024  # Lese letzte 2MB

                with open(self.log_file, "rb") as f:
                    f.seek(-read_size, os.SEEK_END)
                    f.readline()  # Überspringe erste unvollständige Zeile
                    lines = f.read().decode("utf-8", errors="ignore").splitlines()
            else:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    lines = f.readlines()

            result["total_lines"] = len(lines)

            # Filter 1: App-spezifische Logs
            filtered_lines = []
            for line in lines:
                if re.search(pre_defined_log_filter, line, re.IGNORECASE) or re.search(
                    additional_filter, line, re.IGNORECASE
                ):
                    filtered_lines.append(line.rstrip("\n"))

            # Filter 2: Log-Level
            if level_filter:
                level_pattern = rf"\b{re.escape(level_filter)}\b"
                filtered_lines = [
                    line
                    for line in filtered_lines
                    if re.search(level_pattern, line, re.IGNORECASE)
                ]

            # Filter 3: Suchbegriff
            if search_term:
                search_pattern = re.escape(search_term)
                filtered_lines = [
                    line
                    for line in filtered_lines
                    if re.search(search_pattern, line, re.IGNORECASE)
                ]

            result["filtered_lines"] = len(filtered_lines)

            # Neueste zuerst
            filtered_lines.reverse()

            # Limitierung
            if len(filtered_lines) > limit:
                result["has_more"] = True
                filtered_lines = filtered_lines[:limit]

            # Parse Zeilen
            for line in filtered_lines:
                parsed = self._parse_log_line(line)
                result["logs"].append(parsed)

            return result

        except FileNotFoundError:
            print(f"ERROR: Log-Datei nicht gefunden: {self.log_file}")
            return result
        except Exception as e:
            print(f"ERROR beim Lesen der Log-Datei: {e}")
            return result

    def _parse_log_line(self, line):
        """
        Parsed eine Log-Zeile in strukturierte Komponenten

        Format: 2025-11-07 18:26:50,104 [APP-NexusPlayer] [INFO] Nachricht
        """
        pattern = r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})\s+\[([^\]]+)\]\s+\[(INFO|ERROR|WARNING|DEBUG|CRITICAL)\]\s+(.+)$"

        match = re.match(pattern, line.strip())

        if match:
            return {
                "timestamp": match.group(1).strip(),
                "logger": match.group(2).strip(),
                "level": match.group(3).strip(),
                "message": match.group(4).strip(),
                "raw": line,
            }
        else:
            return {
                "timestamp": "",
                "logger": "",
                "level": "UNKNOWN",
                "message": line.strip(),
                "raw": line,
            }

    def get_log_statistics(self):
        """Gibt Statistiken über die Log-Datei zurück"""
        try:
            stats = {
                "total_size_mb": 0,
                "total_lines": 0,
                "app_lines": 0,
                "levels": {
                    "INFO": 0,
                    "ERROR": 0,
                    "WARNING": 0,
                    "DEBUG": 0,
                    "CRITICAL": 0,
                },
                "last_modified": "",
            }

            if not self.log_file.exists():
                return stats

            # Dateigröße
            file_size = self.log_file.stat().st_size
            stats["total_size_mb"] = round(file_size / (1024 * 1024), 2)

            # Letzte Änderung
            from datetime import datetime

            mtime = self.log_file.stat().st_mtime
            stats["last_modified"] = datetime.fromtimestamp(mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # Zeilen-Zählung (nur für kleine Files)
            if file_size < 5 * 1024 * 1024:  # < 5MB
                with open(self.log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        stats["total_lines"] += 1

                        if re.search(self.app_config.logger_name, line, re.IGNORECASE):
                            stats["app_lines"] += 1

                            # Level zählen
                            for level in stats["levels"].keys():
                                if re.search(rf"\b{level}\b", line, re.IGNORECASE):
                                    stats["levels"][level] += 1
                                    break

            return stats

        except Exception as e:
            print(f"ERROR beim Erstellen der Statistiken: {e}")
            return stats

    def get_app_info(self):
        """
        Hole App-Informationen aus app_config

        Returns:
            dict: App-Informationen
        """
        return {
            "app_name": self.app_config.app_name,
            "app_display_name": self.app_config.app_display_name,
            "version": self.app_config.app_version,
            "author": self.app_config.app_author,
            "description": self.app_config.app_description,
            "logger_name": self.app_config.logger_name,
            "logger_level": self.app_config.logger_level,
            "socketio_enabled": self.app_config.socketio_enabled,
            "scheduler_enabled": self.app_config.scheduler_enabled,
            "admin_panel_enabled": self.app_config.admin_panel_enabled,
        }


# ============================================
# STANDALONE HELPER FUNCTIONS
# ============================================


def is_ajax_request():
    """Prüft ob Request von fetch/JavaScript kommt"""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def convert_value(value, original_value):
    """
    Konvertiert String-Wert in korrekten Typ basierend auf Original

    Args:
        value: Neuer Wert als String
        original_value: Original-Wert (bestimmt den Typ)

    Returns:
        Konvertierter Wert im richtigen Typ
    """
    if original_value is None:
        return value

    original_type = type(original_value)

    try:
        if original_type == int:
            return int(value)
        elif original_type == float:
            return float(value)
        elif original_type == bool:
            return value.lower() in ("true", "1", "yes", "on")
        else:
            return value
    except (ValueError, AttributeError):
        return value
