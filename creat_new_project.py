import os
import shutil
from datetime import datetime


def get_current_date_formatted():
    """Gibt das heutige Datum im Format dd.mm.yyyy zurück"""
    today = datetime.now()
    day = today.day
    month = today.month
    year = today.year

    return f"{day:02d}.{month:02d}.{year}"


def replace_template_content(app_path, app_name):
    """Ersetzt Template-Einträge in Dateinamen und Dateiinhalten"""
    template_strings = [
        "Template_app_v000_index",  # Längerer String zuerst
        "Template_app_v000",  # Kürzerer String danach
    ]

    # Aktuelles Datum für README
    current_date = get_current_date_formatted()

    # Liste für umzubenennende Dateien/Ordner
    items_to_rename = []

    # Rekursiv durch alle Dateien und Ordner gehen
    for root, dirs, files in os.walk(app_path):
        # Dateien verarbeiten
        for file in files:
            file_path = os.path.join(root, file)

            # Dateiinhalt ersetzen (nur bei Textdateien)
            try:
                # Versuche als Textdatei zu öffnen
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                content_changed = False

                # Template-Strings ersetzen (längeren zuerst!)
                for template_string in template_strings:
                    if template_string in content:
                        content = content.replace(template_string, app_name)
                        content_changed = True

                # Datumsfelder im README ersetzen
                if file.lower() == "readme.md" or "readme" in file.lower():
                    import re

                    # Created: Datum ersetzen
                    if "Created:" in content:
                        # Erkennt sowohl dd.mm.yyyy als auch dd.mmm.yyyy Format
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
                        print(f"📅 'Created:' Datum aktualisiert auf: {current_date}")

                    # Last Update: Datum ersetzen
                    if "Last Update:" in content:
                        # Erkennt sowohl dd.mm.yyyy als auch dd.mmm.yyyy Format
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
                        print(
                            f"📅 'Last Update:' Datum aktualisiert auf: {current_date}"
                        )

                # Datei nur schreiben wenn sich etwas geändert hat
                if content_changed:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"📝 Inhalt aktualisiert: {file}")

            except (UnicodeDecodeError, PermissionError):
                # Binärdatei oder Datei ohne Leserechte - überspringen
                pass

            # Dateiname prüfen für Umbenennung (beide Template-Strings)
            new_filename = file
            for template_string in template_strings:
                if template_string in new_filename:
                    new_filename = new_filename.replace(template_string, app_name)

            # Wenn sich der Dateiname geändert hat, zur Umbenennung hinzufügen
            if new_filename != file:
                old_path = file_path
                new_path = os.path.join(root, new_filename)
                items_to_rename.append((old_path, new_path, "file"))

        # Ordnernamen prüfen für Umbenennung (beide Template-Strings)
        for dir_name in dirs:
            new_dirname = dir_name
            for template_string in template_strings:
                if template_string in new_dirname:
                    new_dirname = new_dirname.replace(template_string, app_name)

            # Wenn sich der Ordnername geändert hat, zur Umbenennung hinzufügen
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
            print(
                f"{icon} Umbenannt: {os.path.basename(old_path)} → {os.path.basename(new_path)}"
            )
        except Exception as e:
            print(f"⚠️  Fehler beim Umbenennen von {old_path}: {e}")


def create_new_flask_app():
    """Erstellt eine neue Flask App basierend auf dem Template"""

    # Root-Pfad ermitteln
    root_path = os.getcwd()
    apps_path = os.path.join(root_path, "apps")
    template_path = os.path.join(apps_path, "template_app_v000")

    # Überprüfen ob der apps Ordner existiert
    if not os.path.exists(apps_path):
        print(f"Fehler: Der Ordner '{apps_path}' existiert nicht!")
        return

    # Überprüfen ob der Template-Ordner existiert
    if not os.path.exists(template_path):
        print(f"Fehler: Der Template-Ordner '{template_path}' existiert nicht!")
        return

    while True:
        # Benutzer nach dem App-Namen fragen
        app_name = input("Wie soll die neue App heissen? ").strip()

        # Überprüfen ob der Name leer ist
        if not app_name:
            print("Der App-Name darf nicht leer sein!")
            continue

        # Überprüfen ob der erste Buchstabe ein Großbuchstabe ist
        if not app_name[0].isupper():
            print("Der App-Name muss mit einem Großbuchstaben beginnen!")
            continue

        # Überprüfen ob bereits eine App mit diesem Namen existiert
        new_app_path = os.path.join(apps_path, app_name)
        if os.path.exists(new_app_path):
            print(f"Eine App mit dem Namen '{app_name}' existiert bereits!")
            overwrite = input("Möchten Sie sie überschreiben? (j/n): ").strip().lower()
            if overwrite not in ["j", "ja", "y", "yes"]:
                continue
            else:
                # Existierenden Ordner löschen
                shutil.rmtree(new_app_path)

        break

    try:
        # Template-Ordner kopieren
        shutil.copytree(template_path, new_app_path)
        print(f"📁 Template wurde kopiert...")

        # Template-Inhalte anpassen
        replace_template_content(new_app_path, app_name)

        current_date = get_current_date_formatted()
        print(f"✅ Neue Flask App '{app_name}' wurde erfolgreich erstellt!")
        print(f"📅 Alle Datumswerte wurden auf: {current_date} aktualisiert")
        print(f"Pfad: {new_app_path}")

    except Exception as e:
        print(f"❌ Fehler beim Erstellen der App: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("Flask App Template Generator")
    print("=" * 50)
    create_new_flask_app()
