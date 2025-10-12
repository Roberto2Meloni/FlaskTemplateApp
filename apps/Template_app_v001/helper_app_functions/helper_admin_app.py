import re
import os
from .. import logger_name

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


def get_app_logs():
    pre_definded_log_filter = logger_name
    additional_filter = r"\[ ?Reboot FLASK ?\]"  # erlaubt auch optionale Leerzeichen
    log_file = os.path.join(log_path, "server_log.log")

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Behalte Zeilen, die entweder den Logger-Namen oder "[ Reboot FLASK ]" enthalten
        filtered_lines = [
            line
            for line in lines
            if (
                re.search(pre_definded_log_filter, line, re.IGNORECASE)
                or re.search(additional_filter, line, re.IGNORECASE)
            )
        ]

        # Neueste Einträge zuerst
        filtered_lines.reverse()

        return "".join(filtered_lines)

    except FileNotFoundError:
        print(f"ERROR: Log-Datei nicht gefunden: {log_file}")
        return ""
    except Exception as e:
        print(f"ERROR beim Lesen der Log-Datei: {e}")
        return ""
