import re
import os
from .. import logger_name
from flask import request

root__path = os.getcwd()
app_path = os.path.join(
    root__path, "app", "imported_apps", "develop_release", "Template_app_v001"
)
log_path = os.path.join(root__path, "log")
log_file = os.path.join(log_path, "server_log.log")
readme_file = os.path.join(app_path, "README.md")


def get_app_info():
    """
    Liest die README.md und extrahiert alle App-Informationen.

    Returns:
        dict: Dictionary mit allen App-Informationen
    """
    app_info = {
        "app_name": "",
        "author": "",
        "created": "",
        "last_update": "",
        "last_version": "",
        "system_requirements": "",
        "description": "",
        "category": "",
        "tags": "",
        "repository_url": "",
        "other": "",
    }

    try:
        with open(readme_file, "r", encoding="utf-8") as f:
            readme = f.read()

        # Mapping: README-Key → Dict-Key
        mappings = {
            "Name": "app_name",
            "Author": "author",
            "Created": "created",
            "Last Update": "last_update",
            "Last Version": "last_version",
            "System Requirements": "system_requirements",
            "Description": "description",
            "Category": "category",
            "Tags": "tags",
            "Repository URL": "repository_url",
            "Other": "other",
        }

        # Für jeden Mapping-Eintrag suchen
        for readme_key, dict_key in mappings.items():
            # Pattern: "Key: Value" (ohne Prefix wie ## oder ***)
            pattern = rf"^{re.escape(readme_key)}:\s*(.+)$"
            match = re.search(pattern, readme, re.MULTILINE | re.IGNORECASE)

            if match:
                app_info[dict_key] = match.group(1).strip()

        return app_info

    except FileNotFoundError:
        print(f"ERROR: README.md nicht gefunden: {readme_file}")
        return app_info
    except Exception as e:
        print(f"ERROR beim Lesen der README: {e}")
        return app_info


def get_app_logs(limit=500, level_filter=None, search_term=None):
    """
    Liest App-Logs effizient - nur die letzten N Zeilen

    Args:
        limit (int): Anzahl der Log-Zeilen die zurückgegeben werden sollen
        level_filter (str): Filter nach Log-Level (INFO, ERROR, WARNING, DEBUG)
        search_term (str): Suchbegriff zum Filtern

    Returns:
        dict: Dictionary mit Log-Informationen
    """
    pre_defined_log_filter = logger_name
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
        file_size = os.path.getsize(log_file)
        result["file_size_mb"] = round(file_size / (1024 * 1024), 2)

        # Effiziente Rückwärts-Lesung: Lese nur die letzten Bytes
        # Bei großen Files (>10MB) nur die letzten 2MB lesen
        if file_size > 10 * 1024 * 1024:  # > 10MB
            read_size = 2 * 1024 * 1024  # Lese letzte 2MB

            with open(log_file, "rb") as f:
                f.seek(-read_size, os.SEEK_END)
                # Überspringe die erste unvollständige Zeile
                f.readline()
                lines = f.read().decode("utf-8", errors="ignore").splitlines()
        else:
            # Bei kleinen Files alles lesen
            with open(log_file, "r", encoding="utf-8") as f:
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

        # Neueste zuerst (reverse)
        filtered_lines.reverse()

        # Limitierung
        if len(filtered_lines) > limit:
            result["has_more"] = True
            filtered_lines = filtered_lines[:limit]

        # Parse jede Zeile in strukturierte Form
        for line in filtered_lines:
            parsed = parse_log_line(line)
            result["logs"].append(parsed)

        return result

    except FileNotFoundError:
        print(f"ERROR: Log-Datei nicht gefunden: {log_file}")
        return result
    except Exception as e:
        print(f"ERROR beim Lesen der Log-Datei: {e}")
        return result


def parse_log_line(line):
    """
    Parsed eine Log-Zeile in strukturierte Komponenten

    Format: 2025-11-07 18:26:50,104 [APP-NexusPlayer] [INFO] Nachricht

    Returns:
        dict: Strukturierte Log-Daten
    """
    # Pattern mit eckigen Klammern und Millisekunden
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
        # Fallback: Unstrukturierte Zeile
        return {
            "timestamp": "",
            "logger": "",
            "level": "UNKNOWN",
            "message": line.strip(),
            "raw": line,
        }


def convert_value(value, original_value):
    """
    Konvertiert einen String-Wert in den korrekten Typ basierend auf dem Original
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


def is_ajax_request():
    """
    Prüft ob der Request von fetch/JavaScript kommt
    """
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


def get_log_statistics():
    """
    Gibt Statistiken über die Log-Datei zurück
    """
    try:
        stats = {
            "total_size_mb": 0,
            "total_lines": 0,
            "app_lines": 0,
            "levels": {"INFO": 0, "ERROR": 0, "WARNING": 0, "DEBUG": 0, "CRITICAL": 0},
            "last_modified": "",
        }

        if not os.path.exists(log_file):
            return stats

        # Dateigröße
        file_size = os.path.getsize(log_file)
        stats["total_size_mb"] = round(file_size / (1024 * 1024), 2)

        # Letzte Änderung
        from datetime import datetime

        mtime = os.path.getmtime(log_file)
        stats["last_modified"] = datetime.fromtimestamp(mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Schnelle Zeilen-Zählung (nur für kleine Files)
        if file_size < 5 * 1024 * 1024:  # < 5MB
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    stats["total_lines"] += 1

                    if re.search(logger_name, line, re.IGNORECASE):
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
