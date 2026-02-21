"""
Flask App Update Script
Aktualisiert alle Apps im apps/ Ordner die Template_Base: 002 verwenden.

Wie die Version gesteuert wird:
  → _BASE_VERSION in Template_app_v002/_base/config/app_config.py setzen
  → Script kopiert _base/ komplett → Version wird automatisch mitgenommen
  → AppConfig synct beim nächsten App-Start die neue Version ins JSON

Was wird aktualisiert:
  - _base/ Ordner komplett ersetzt (aus Template_app_v002/_base/)
  - Dateinamen angepasst (Template_app_v002 → AppName)
  - Dateiinhalte angepasst (Template_app_v002 → AppName)
  - README: Last Update Datum

Was NICHT angerührt wird:
  - _custom/
  - static/_custom/
  - templates/_custom/
  - models.py, __init__.py, icon.png, requirements.txt
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional


# ========================================
# KONFIGURATION
# ========================================

TEMPLATE_NAME = "Template_app_v002"
REQUIRED_BASE = "002"


# ========================================
# HILFSFUNKTIONEN
# ========================================


def get_current_date() -> str:
    today = datetime.now()
    return f"{today.day:02d}.{today.month:02d}.{today.year}"


def read_readme(app_path: Path) -> Optional[str]:
    readme = app_path / "README.md"
    if readme.exists():
        try:
            return readme.read_text(encoding="utf-8")
        except Exception:
            return None
    return None


def get_template_base(readme_content: str) -> Optional[str]:
    match = re.search(r"Template_Base:\s*(\S+)", readme_content)
    return match.group(1).strip() if match else None


def get_app_name_from_readme(readme_content: str) -> Optional[str]:
    match = re.search(r"^Name:\s*(.+)$", readme_content, re.MULTILINE)
    return match.group(1).strip() if match else None


def read_base_version_from_template(template_path: Path) -> str:
    """Liest _BASE_VERSION aus Template app_config.py — nur für Anzeige"""
    config_path = template_path / "_base" / "config" / "app_config.py"
    if config_path.exists():
        try:
            content = config_path.read_text(encoding="utf-8")
            match = re.search(r'_BASE_VERSION\s*=\s*"([^"]+)"', content)
            if match:
                return match.group(1)
        except Exception:
            pass
    return "unbekannt"


def update_readme_date(app_path: Path) -> None:
    readme = app_path / "README.md"
    if not readme.exists():
        return
    content = readme.read_text(encoding="utf-8")
    today = get_current_date()
    content = re.sub(
        r"(Last Update:\s*)[\d]{1,2}\.[\d]{1,2}\.[\d]{4}", f"\\g<1>{today}", content
    )
    readme.write_text(content, encoding="utf-8")
    print(f"   📅 README Last Update → {today}")


# ========================================
# KERN: _BASE KOPIEREN & ANPASSEN
# ========================================


def replace_content(content: str, app_name: str) -> str:
    """Ersetzt Template_app_v002 → AppName im Dateiinhalt"""
    content = content.replace(TEMPLATE_NAME, app_name)
    # AppLogger uppercase
    content = re.sub(
        rf'AppLogger\("APP-{app_name}"\)',
        f'AppLogger("APP-{app_name.upper()}")',
        content,
    )
    return content


def copy_and_adapt_base(template_base: Path, target_base: Path, app_name: str) -> int:
    """
    Kopiert _base/ vom Template und passt Inhalte + Namen an.
    Gibt Anzahl verarbeiteter Dateien zurück.
    """
    file_count = 0
    items_to_rename = []

    # PASS 1: Kopieren + Dateiinhalte ersetzen
    for src_file in template_base.rglob("*"):
        if src_file.is_dir():
            continue

        rel_path = src_file.relative_to(template_base)
        dst_file = target_base / rel_path
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)

        # Textdateien anpassen
        try:
            content = dst_file.read_text(encoding="utf-8")
            new_content = replace_content(content, app_name)
            if new_content != content:
                dst_file.write_text(new_content, encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            pass

        file_count += 1

        if TEMPLATE_NAME in dst_file.name:
            items_to_rename.append(dst_file)

    # PASS 2: Ordner mit Template-Namen sammeln
    for dir_path in target_base.rglob("*"):
        if dir_path.is_dir() and TEMPLATE_NAME in dir_path.name:
            items_to_rename.append(dir_path)

    # PASS 3: Umbenennen — tiefstes Level zuerst
    items_to_rename.sort(key=lambda p: len(p.parts), reverse=True)
    for old_path in items_to_rename:
        if old_path.exists() and TEMPLATE_NAME in old_path.name:
            new_path = old_path.parent / old_path.name.replace(TEMPLATE_NAME, app_name)
            try:
                old_path.rename(new_path)
            except Exception as e:
                print(f"   ⚠️  Umbenennen fehlgeschlagen {old_path.name}: {e}")

    return file_count


def update_app(app_path: Path, app_name: str, template_path: Path) -> bool:
    """Aktualisiert eine einzelne App."""
    template_base = template_path / "_base"
    target_base = app_path / "_base"

    if not template_base.exists():
        print(f"   ❌ Template _base/ nicht gefunden: {template_base}")
        return False

    # 1. Backup des aktuellen _base/
    backup_path = app_path / "_base_backup"
    if backup_path.exists():
        shutil.rmtree(backup_path)

    if target_base.exists():
        shutil.copytree(target_base, backup_path)
        print(f"   💾 Backup erstellt: _base_backup/")

    # 2. Altes _base/ löschen
    if target_base.exists():
        shutil.rmtree(target_base)

    # 3. Neues _base/ kopieren und anpassen
    try:
        file_count = copy_and_adapt_base(template_base, target_base, app_name)
        print(f"   📁 _base/ aktualisiert ({file_count} Dateien)")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        # Rollback
        if backup_path.exists():
            shutil.copytree(backup_path, target_base)
            print(f"   🔄 Rollback durchgeführt")
        return False

    # 4. README Datum aktualisieren
    update_readme_date(app_path)

    # 5. Backup entfernen
    if backup_path.exists():
        shutil.rmtree(backup_path)
        print(f"   🗑️  Backup entfernt")

    return True


# ========================================
# SCAN: APPS MIT Template_Base: 002 FINDEN
# ========================================


def scan_apps(apps_path: Path) -> list:
    candidates = []
    for entry in sorted(apps_path.iterdir()):
        if not entry.is_dir() or entry.name == TEMPLATE_NAME:
            continue

        readme = read_readme(entry)
        if not readme:
            continue

        if get_template_base(readme) != REQUIRED_BASE:
            continue

        candidates.append((entry, entry.name))

    return candidates


# ========================================
# HAUPTPROGRAMM
# ========================================


def main() -> None:
    root_path = Path(os.getcwd())
    apps_path = root_path / "apps"
    template_path = apps_path / TEMPLATE_NAME

    # Aktuelle Version aus Template lesen (nur für Anzeige)
    new_version = read_base_version_from_template(template_path)

    print("=" * 60)
    print("🔄  Flask App Update Script")
    print(f"    Template:     {TEMPLATE_NAME}")
    print(f"    _BASE_VERSION: {new_version}")
    print(f"    Filter:       Template_Base: {REQUIRED_BASE}")
    print("=" * 60)

    # Pfade prüfen
    if not apps_path.exists():
        print(f"❌ apps/ Ordner nicht gefunden: {apps_path}")
        return

    if not template_path.exists():
        print(f"❌ Template nicht gefunden: {template_path}")
        return

    # Apps scannen
    print(f"\n🔍 Scanne apps/ ...")
    candidates = scan_apps(apps_path)

    if not candidates:
        print(f"\n   Keine Apps mit Template_Base: {REQUIRED_BASE} gefunden.")
        return

    print(f"\n📋 Gefundene Apps ({len(candidates)}):")
    for _, app_name in candidates:
        print(f"   • {app_name}")

    # Bestätigung
    print(f"\n{'─' * 60}")
    print(f"⚠️  Folgendes wird überschrieben:")
    print(f"   - _base/ komplett (Version: {new_version})")
    print(f"   - README Last Update Datum → {get_current_date()}")
    print(f"\n   Nicht verändert: _custom/, models.py, __init__.py")
    print(f"{'─' * 60}")

    confirm = input("\nUpdate starten? (j/n): ").strip().lower()
    if confirm not in ["j", "ja", "y", "yes"]:
        print("⏹️  Abgebrochen.")
        return

    # Updates durchführen
    success_count = 0
    failed = []

    for app_path, app_name in candidates:
        print(f"\n{'─' * 60}")
        print(f"🔨 Update: {app_name}")
        if update_app(app_path, app_name, template_path):
            success_count += 1
            print(f"   ✅ {app_name} erfolgreich aktualisiert")
        else:
            failed.append(app_name)

    # Zusammenfassung
    print(f"\n{'=' * 60}")
    print(f"📊 Zusammenfassung:")
    print(f"   ✅ Erfolgreich: {success_count}/{len(candidates)}")
    if failed:
        print(f"   ❌ Fehlgeschlagen: {', '.join(failed)}")
    print(f"\n💡 Nächster Schritt:")
    print(f"   Apps neu starten → AppConfig synct _BASE_VERSION ins JSON")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
