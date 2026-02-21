"""
Flask App Template Generator
Erstellt neue Apps basierend auf Template_app_v002

Struktur: _base / _custom Ordner
Template:  Template_app_v002
"""

import os
import shutil
import re
from datetime import datetime
from typing import List, Tuple


TEMPLATE_NAME = "Template_app_v002"


# ========================================
# HILFSFUNKTIONEN
# ========================================


def get_current_date_formatted() -> str:
    """Gibt das heutige Datum im Format dd.mm.yyyy zurück"""
    today = datetime.now()
    return f"{today.day:02d}.{today.month:02d}.{today.year}"


def validate_app_name(app_name: str) -> Tuple[bool, str]:
    """Validiert den App-Namen"""
    if not app_name:
        return False, "Der App-Name darf nicht leer sein!"
    if not app_name[0].isupper():
        return False, "Der App-Name muss mit einem Grossbuchstaben beginnen!"
    if " " in app_name:
        return False, "Der App-Name darf keine Leerzeichen enthalten!"
    if not app_name.replace("_", "").isalnum():
        return (
            False,
            "Der App-Name darf nur Buchstaben, Zahlen und Unterstriche enthalten!",
        )
    return True, ""


# ========================================
# KERN: TEMPLATE-ERSETZUNG
# ========================================


def replace_in_file(file_path: str, app_name: str, current_date: str) -> bool:
    """
    Ersetzt alle Template-Referenzen im Dateiinhalt.
    Gibt True zurück wenn Änderungen gemacht wurden.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError, IsADirectoryError):
        return False

    original = content

    # ----------------------------------------
    # 1. Hauptersetzung: Template_app_v002 → AppName
    # ----------------------------------------
    content = content.replace(TEMPLATE_NAME, app_name)

    # ----------------------------------------
    # 2. Python-spezifische Anpassungen
    # ----------------------------------------
    if file_path.endswith(".py"):

        # Blueprint Name
        content = re.sub(
            rf'Blueprint\(\s*"{app_name}"', f'Blueprint(\n    "{app_name}"', content
        )

        # url_prefix
        content = re.sub(
            rf'url_prefix="/{app_name}"', f'url_prefix="/{app_name}"', content
        )

        # static_url_path
        content = re.sub(
            rf'static_url_path="/{app_name}_static"',
            f'static_url_path="/{app_name}_static"',
            content,
        )

        # AppLogger - UPPERCASE für Logger-Name
        content = re.sub(
            rf'AppLogger\("APP-{app_name}"\)',
            f'AppLogger("APP-{app_name.upper()}")',
            content,
        )

        # APP_NAME Variable
        content = re.sub(
            rf'APP_NAME\s*=\s*"{app_name}"', f'APP_NAME = "{app_name}"', content
        )

    # ----------------------------------------
    # 3. README Datum anpassen
    # ----------------------------------------
    if os.path.basename(file_path).lower() == "readme.md":
        content = re.sub(
            r"Created:\s*[\d]{1,2}\.[\d]{1,2}\.[\d]{4}",
            f"Created: {current_date}",
            content,
        )
        content = re.sub(
            r"Last Update:\s*[\d]{1,2}\.[\d]{1,2}\.[\d]{4}",
            f"Last Update: {current_date}",
            content,
        )

    if content != original:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    return False


def rename_item(old_path: str, app_name: str) -> str:
    """
    Benennt Datei/Ordner um wenn Template-Name enthalten.
    Gibt neuen Pfad zurück (oder alten wenn keine Änderung).
    """
    dirname = os.path.dirname(old_path)
    basename = os.path.basename(old_path)

    if TEMPLATE_NAME not in basename:
        return old_path

    new_basename = basename.replace(TEMPLATE_NAME, app_name)
    new_path = os.path.join(dirname, new_basename)

    try:
        os.rename(old_path, new_path)
        print(f"   📄 {basename} → {new_basename}")
        return new_path
    except Exception as e:
        print(f"   ⚠️  Fehler beim Umbenennen von {basename}: {e}")
        return old_path


def process_app_directory(app_path: str, app_name: str) -> None:
    """
    Verarbeitet das komplette App-Verzeichnis:
    1. Alle Dateiinhalte ersetzen
    2. Alle Datei- und Ordnernamen umbenennen
    """
    current_date = get_current_date_formatted()
    files_updated = 0
    items_to_rename: List[Tuple[str, str]] = []  # (old_path, item_type)

    # ----------------------------------------
    # PASS 1: Dateiinhalte ersetzen
    # ----------------------------------------
    print(f"\n   🔄 Ersetze Dateiinhalte...")
    for root, dirs, files in os.walk(app_path):
        # Versteckte Ordner überspringen
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for filename in files:
            file_path = os.path.join(root, filename)
            changed = replace_in_file(file_path, app_name, current_date)
            if changed:
                files_updated += 1

    print(f"   ✓ {files_updated} Dateien aktualisiert")

    # ----------------------------------------
    # PASS 2: Umbenennen (tiefstes Level zuerst)
    # ----------------------------------------
    print(f"   🔄 Benenne Dateien und Ordner um...")
    rename_count = 0

    for root, dirs, files in os.walk(app_path, topdown=False):
        # Dateien umbenennen
        for filename in files:
            if TEMPLATE_NAME in filename:
                old_path = os.path.join(root, filename)
                items_to_rename.append((old_path, "file"))

        # Ordner umbenennen (tiefste zuerst durch topdown=False)
        for dirname in dirs:
            if TEMPLATE_NAME in dirname:
                old_path = os.path.join(root, dirname)
                items_to_rename.append((old_path, "dir"))

    # Tiefste Pfade zuerst (längster Pfad = tiefste Ebene)
    items_to_rename.sort(key=lambda x: x[0].count(os.sep), reverse=True)

    for old_path, _ in items_to_rename:
        if os.path.exists(
            old_path
        ):  # Prüfen ob noch vorhanden (Parent schon umbenannt?)
            rename_item(old_path, app_name)
            rename_count += 1

    print(f"   ✓ {rename_count} Elemente umbenannt")


# ========================================
# HAUPTFUNKTION: EINE APP ERSTELLEN
# ========================================


def create_app(app_name: str, apps_path: str, template_path: str) -> bool:
    """
    Erstellt eine einzelne neue App.
    Gibt True zurück wenn erfolgreich.
    """
    new_app_path = os.path.join(apps_path, app_name)

    # Existenz prüfen
    if os.path.exists(new_app_path):
        print(f"\n   ⚠️  '{app_name}' existiert bereits in apps/")
        overwrite = input("   Überschreiben? (j/n): ").strip().lower()
        if overwrite not in ["j", "ja", "y", "yes"]:
            print(f"   ⏭️  '{app_name}' übersprungen")
            return False
        try:
            shutil.rmtree(new_app_path)
            print(f"   🗑️  Alte Version gelöscht")
        except Exception as e:
            print(f"   ❌ Fehler beim Löschen: {e}")
            return False

    try:
        # Template kopieren
        print(f"   📋 Kopiere Template...")
        shutil.copytree(template_path, new_app_path)

        # Inhalt verarbeiten
        process_app_directory(new_app_path, app_name)

        print(f"   📂 Pfad: {new_app_path}")
        return True

    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        import traceback

        traceback.print_exc()

        # Aufräumen bei Fehler
        if os.path.exists(new_app_path):
            shutil.rmtree(new_app_path)
        return False


# ========================================
# EINSTIEGSPUNKT
# ========================================


def main() -> None:
    """Hauptprogramm"""
    root_path = os.getcwd()
    apps_path = os.path.join(root_path, "apps")
    template_path = os.path.join(apps_path, TEMPLATE_NAME)

    print("=" * 55)
    print("🚀  Flask App Generator")
    print(f"    Template: {TEMPLATE_NAME}")
    print("=" * 55)

    # Pfade prüfen
    if not os.path.exists(apps_path):
        print(f"❌ Ordner 'apps/' nicht gefunden unter: {root_path}")
        return

    if not os.path.exists(template_path):
        print(f"❌ Template nicht gefunden: {template_path}")
        return

    # Anzahl Apps
    while True:
        try:
            count_input = input("\nWie viele Apps möchtest du erstellen? [1]: ").strip()
            app_count = int(count_input) if count_input else 1
            if app_count < 1:
                print("❌ Mindestens 1 App!")
                continue
            break
        except ValueError:
            print("❌ Bitte eine Zahl eingeben!")

    # App-Namen sammeln
    app_names: List[str] = []

    for i in range(app_count):
        prefix = f"[{i+1}/{app_count}] " if app_count > 1 else ""
        while True:
            app_name = input(f"\n{prefix}App-Name: ").strip()
            is_valid, error = validate_app_name(app_name)
            if not is_valid:
                print(f"   ❌ {error}")
                continue
            if app_name in app_names:
                print(f"   ❌ '{app_name}' wurde bereits eingegeben!")
                continue
            app_names.append(app_name)
            break

    # Bestätigung
    print(f"\n{'─' * 55}")
    print(f"📋 Folgende Apps werden erstellt:")
    for name in app_names:
        target = os.path.join(apps_path, name)
        exists = " (existiert bereits → wird gefragt)" if os.path.exists(target) else ""
        print(f"   • {name}{exists}")
    print(f"{'─' * 55}")

    confirm = input("\nFortfahren? (j/n): ").strip().lower()
    if confirm not in ["j", "ja", "y", "yes"]:
        print("⏹️  Abgebrochen.")
        return

    # Apps erstellen
    success_count = 0
    failed: List[str] = []

    for app_name in app_names:
        print(f"\n{'─' * 55}")
        print(f"🔨 Erstelle: {app_name}")
        success = create_app(app_name, apps_path, template_path)
        if success:
            success_count += 1
            print(f"   ✅ {app_name} erfolgreich erstellt!")
        else:
            failed.append(app_name)

    # Zusammenfassung
    print(f"\n{'=' * 55}")
    print(f"📊 Zusammenfassung:")
    print(f"   ✅ Erfolgreich: {success_count}/{len(app_names)}")
    if failed:
        print(f"   ❌ Fehlgeschlagen: {', '.join(failed)}")

    if success_count > 0:
        print(f"\n💡 Nächste Schritte:")
        print(f"   1. Apps in app/__init__.py registrieren:")
        for name in app_names:
            if name not in failed:
                print(f"      from apps.{name} import blueprint as {name}_bp")
        print(f"   2. Blueprint registrieren: app.register_blueprint({name}_bp)")

    print(f"{'=' * 55}\n")


if __name__ == "__main__":
    main()
