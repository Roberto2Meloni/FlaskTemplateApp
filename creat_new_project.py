import os
import shutil
import re
from datetime import datetime
from typing import List, Tuple


def get_current_date_formatted() -> str:
    """Gibt das heutige Datum im Format dd.mm.yyyy zurück"""
    today = datetime.now()
    return f"{today.day:02d}.{today.month:02d}.{today.year}"


def replace_template_content(app_path: str, app_name: str) -> None:
    """Ersetzt Template-Einträge in Dateinamen und Dateiinhalten"""

    # Template-Strings mit ihren Ersetzungen definieren
    template_replacements = [
        ("Template_app_v000_index", f"{app_name}_index"),  # Mit _index Suffix
        ("Template_app_v000", app_name),  # Ohne Suffix
    ]

    current_date = get_current_date_formatted()
    items_to_rename: List[Tuple[str, str, str]] = []

    # Rekursiv durch alle Dateien und Ordner gehen
    for root, dirs, files in os.walk(app_path):
        # Dateien verarbeiten
        for file in files:
            file_path = os.path.join(root, file)

            # Dateiinhalt ersetzen (nur bei Textdateien)
            content_changed = False
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Template-Strings ersetzen (längeren zuerst!)
                for template_str, replacement in template_replacements:
                    if template_str in content:
                        content = content.replace(template_str, replacement)
                        content_changed = True

                # Spezielle Ersetzung für HTML-Referenzen in render_template()
                # Template_app_v000_index.html → AppName.html (ohne _index)
                html_template_pattern = "Template_app_v000_index.html"
                html_replacement = f"{app_name}.html"
                if html_template_pattern in content:
                    content = content.replace(html_template_pattern, html_replacement)
                    content_changed = True

                # Auch Template_app_v000.html → AppName.html
                html_template_pattern2 = "Template_app_v000.html"
                if html_template_pattern2 in content:
                    content = content.replace(html_template_pattern2, html_replacement)
                    content_changed = True

                # Blueprint und AppLogger Anpassungen (nur in Python-Dateien)
                if file.endswith(".py"):
                    # Blueprint name und url_prefix anpassen
                    # Blueprint("Test05", ... ) → Blueprint("AppName", ... )
                    blueprint_pattern = r'Blueprint\(\s*"Template_app_v000"'
                    if re.search(blueprint_pattern, content):
                        content = re.sub(
                            blueprint_pattern, f'Blueprint(\n    "{app_name}"', content
                        )
                        content_changed = True

                    # url_prefix="/Template_app_v000" → url_prefix="/AppName"
                    url_prefix_pattern = r'url_prefix="/Template_app_v000"'
                    if re.search(url_prefix_pattern, content):
                        content = re.sub(
                            url_prefix_pattern, f'url_prefix="/{app_name}"', content
                        )
                        content_changed = True

                    # static_url_path="/Template_app_v000_static" → static_url_path="/AppName_static"
                    static_url_pattern = r'static_url_path="/Template_app_v000_static"'
                    if re.search(static_url_pattern, content):
                        content = re.sub(
                            static_url_pattern,
                            f'static_url_path="/{app_name}_static"',
                            content,
                        )
                        content_changed = True

                    # AppLogger("APP-TEMPLATE_APP_V000") → AppLogger("APP-APPNAME")
                    # App-Name in Großbuchstaben für Logger
                    app_logger_pattern = r'AppLogger\("APP-TEMPLATE_APP_V000"\)'
                    if re.search(app_logger_pattern, content):
                        content = re.sub(
                            app_logger_pattern,
                            f'AppLogger("APP-{app_name.upper()}")',
                            content,
                        )
                        content_changed = True

                # Datumsfelder im README ersetzen
                if "readme" in file.lower():
                    if "Created:" in content:
                        content = re.sub(
                            r"Created:\s*\d{1,2}\.\d{1,2}\.\d{4}",
                            f"Created: {current_date}",
                            content,
                        )
                        content = re.sub(
                            r"Created:\s*\d{1,2}\.\w{3}\.\d{4}",
                            f"Created: {current_date}",
                            content,
                        )
                        content_changed = True

                    if "Last Update:" in content:
                        content = re.sub(
                            r"Last Update:\s*\d{1,2}\.\d{1,2}\.\d{4}",
                            f"Last Update: {current_date}",
                            content,
                        )
                        content = re.sub(
                            r"Last Update:\s*\d{1,2}\.\w{3}\.\d{4}",
                            f"Last Update: {current_date}",
                            content,
                        )
                        content_changed = True

                # Datei nur schreiben wenn sich etwas geändert hat
                if content_changed:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"📝 Inhalt aktualisiert: {file}")

            except (UnicodeDecodeError, PermissionError):
                pass

            # Dateiname prüfen für Umbenennung
            new_filename = file

            # Spezielle Behandlung für HTML-Dateien: kein _index Suffix
            if file.lower().endswith(".html"):
                if "Template_app_v000_index" in new_filename:
                    new_filename = new_filename.replace(
                        "Template_app_v000_index", app_name
                    )
                elif "Template_app_v000" in new_filename:
                    new_filename = new_filename.replace("Template_app_v000", app_name)
            else:
                # Für alle anderen Dateien: normale Ersetzungsregeln
                for template_str, replacement in template_replacements:
                    if template_str in new_filename:
                        new_filename = new_filename.replace(template_str, replacement)

            # Wenn sich der Dateiname geändert hat, zur Umbenennung hinzufügen
            if new_filename != file:
                old_path = file_path
                new_path = os.path.join(root, new_filename)
                items_to_rename.append((old_path, new_path, "file"))

        # Ordnernamen prüfen für Umbenennung
        for dir_name in dirs:
            new_dirname = dir_name
            for template_str, replacement in template_replacements:
                if template_str in new_dirname:
                    new_dirname = new_dirname.replace(template_str, replacement)

            if new_dirname != dir_name:
                old_path = os.path.join(root, dir_name)
                new_path = os.path.join(root, new_dirname)
                items_to_rename.append((old_path, new_path, "dir"))

    # Umbenennung durchführen (von tiefstem Level nach oben)
    items_to_rename.sort(key=lambda x: x[0].count(os.sep), reverse=True)
    for old_path, new_path, item_type in items_to_rename:
        try:
            os.rename(old_path, new_path)
            icon = "📁" if item_type == "dir" else "📄"
            old_name = os.path.basename(old_path)
            new_name = os.path.basename(new_path)
            print(f"{icon} Umbenannt: {old_name} → {new_name}")
        except Exception as e:
            print(f"⚠️  Fehler beim Umbenennen von {old_path}: {e}")


def modify_route(app_name: str) -> bool:
    """
    Fügt die neue App-Route zur routes.py Datei hinzu.

    Ersetzt die Template-Route durch die neue App-Route:
    - Route: /Template_app_v000_index → /AppName_index
    - Funktion: Template_app_v000_index() → AppName_index()
    - HTML: Template_app_v000.html → AppName.html (OHNE _index)

    Args:
        app_name: Name der neuen App

    Returns:
        bool: True wenn erfolgreich, False bei Fehler
    """
    route_file = os.path.join(os.getcwd(), "routes.py")

    if not os.path.exists(route_file):
        print(f"⚠️  Warnung: routes.py nicht gefunden unter {route_file}")
        return False

    try:
        # Datei einlesen
        with open(route_file, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # 1. Route-Pfad ersetzen: /Template_app_v000_index → /AppName_index
        content = content.replace(
            '@blueprint.route("/Template_app_v000_index"',
            f'@blueprint.route("/{app_name}_index"',
        )

        # 2. Funktionsname ersetzen: def Template_app_v000_index() → def AppName_index()
        content = content.replace(
            "def Template_app_v000_index():", f"def {app_name}_index():"
        )

        # 3. HTML-Template-Referenz ersetzen: Template_app_v000.html → AppName.html
        content = re.sub(
            r'"Template_app_v000(_index)?\.html"', f'"{app_name}.html"', content
        )

        # Prüfen ob Änderungen vorgenommen wurden
        if content != original_content:
            # Datei speichern
            with open(route_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ routes.py wurde aktualisiert")
            print(f"   Route: /{app_name}_index")
            print(f"   Funktion: {app_name}_index()")
            print(f"   Template: {app_name}.html")
            return True
        else:
            print(f"ℹ️  Keine Template-Route in routes.py gefunden")
            return False

    except Exception as e:
        print(f"❌ Fehler beim Modifizieren von routes.py: {e}")
        return False


def validate_app_name(app_name: str) -> Tuple[bool, str]:
    """
    Validiert den App-Namen.

    Returns:
        Tuple[bool, str]: (ist_gültig, fehlermeldung)
    """
    if not app_name:
        return False, "Der App-Name darf nicht leer sein!"

    if not app_name[0].isupper():
        return False, "Der App-Name muss mit einem Großbuchstaben beginnen!"

    if " " in app_name:
        return False, "Der App-Name darf keine Leerzeichen enthalten!"

    if not app_name.replace("_", "").isalnum():
        return (
            False,
            "Der App-Name darf nur Buchstaben, Zahlen und Unterstriche enthalten!",
        )

    return True, ""


def create_new_flask_app() -> None:
    """Erstellt eine neue Flask App basierend auf dem Template"""

    # Root-Pfad ermitteln
    root_path = os.getcwd()
    apps_path = os.path.join(root_path, "apps")
    template_path = os.path.join(apps_path, "template_app_v000")

    # Überprüfen ob der apps Ordner existiert
    if not os.path.exists(apps_path):
        print(f"❌ Fehler: Der Ordner '{apps_path}' existiert nicht!")
        return

    # Überprüfen ob der Template-Ordner existiert
    if not os.path.exists(template_path):
        print(f"❌ Fehler: Der Template-Ordner '{template_path}' existiert nicht!")
        return

    while True:
        # Benutzer nach dem App-Namen fragen
        app_name = input("\nWie soll die neue App heissen? ").strip()

        # Name validieren
        is_valid, error_message = validate_app_name(app_name)
        if not is_valid:
            print(f"❌ {error_message}")
            continue

        # Überprüfen ob bereits eine App mit diesem Namen existiert
        new_app_path = os.path.join(apps_path, app_name)
        if os.path.exists(new_app_path):
            print(f"⚠️  Eine App mit dem Namen '{app_name}' existiert bereits!")
            overwrite = input("Möchten Sie sie überschreiben? (j/n): ").strip().lower()
            if overwrite not in ["j", "ja", "y", "yes"]:
                continue
            else:
                try:
                    shutil.rmtree(new_app_path)
                    print(f"🗑️  Alte App wurde gelöscht.")
                except Exception as e:
                    print(f"❌ Fehler beim Löschen der alten App: {e}")
                    return

        break

    try:
        # Template-Ordner kopieren
        print(f"\n📋 Kopiere Template...")
        shutil.copytree(template_path, new_app_path)
        print(f"✓ Template wurde kopiert")

        # Template-Inhalte anpassen
        print(f"\n🔄 Passe Template-Inhalte an...")
        replace_template_content(new_app_path, app_name)

        # routes.py modifizieren
        print(f"\n🔧 Aktualisiere routes.py...")
        modify_route(app_name)

        current_date = get_current_date_formatted()
        print(f"\n{'=' * 50}")
        print(f"✅ Neue Flask App '{app_name}' wurde erfolgreich erstellt!")
        print(f"📅 Alle Datumswerte wurden auf: {current_date} aktualisiert")
        print(f"📂 Pfad: {new_app_path}")
        print(f"{'=' * 50}")

    except Exception as e:
        print(f"\n❌ Fehler beim Erstellen der App: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Flask App Template Generator")
    print("=" * 50)
    create_new_flask_app()
