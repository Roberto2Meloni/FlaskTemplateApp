"""
Flask App Update Script
Aktualisiert alle Apps im apps/ Ordner die Template_Base: 002 verwenden.

Versionierung:
  - admin_app_version: kommt aus _BASE_VERSION im kopierten app_config.py (readonly)
  - app_version:       wird vom Script um 0.0.1 erhöht (im JSON + README)
                       jede App hat ihre eigene app_version — das ist korrekt so

Was wird aktualisiert:
  - _base/ Ordner komplett ersetzt
  - Dateinamen + Inhalte angepasst (Template_app_v002 → AppName)
  - app_version im JSON um 0.0.1 erhöht
  - README: Last Update + Last Version synchronisiert

Was NICHT angerührt wird:
  - _custom/, models.py, __init__.py, icon.png, requirements.txt
"""

import json
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
# VERSIONS-HILFSFUNKTIONEN
# ========================================


def increment_version(version: str) -> str:
    """
    Erhöht Patch-Version um 1.
    "0.0.4" → "0.0.5"
    "0.0.9" → "0.1.0"
    "1.9.9" → "2.0.0"
    """
    try:
        parts = version.strip().split(".")
        if len(parts) != 3:
            return "0.0.1"
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        patch += 1
        if patch >= 10:
            patch = 0
            minor += 1
        if minor >= 10:
            minor = 0
            major += 1
        return f"{major}.{minor}.{patch}"
    except (ValueError, AttributeError):
        return "0.0.1"


def read_app_version_from_json(app_path: Path) -> str:
    """Liest aktuelle app_version aus dem _custom JSON"""
    json_path = app_path / "_custom" / "config" / "app_config.json"
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("app_version", "0.0.0")
        except Exception:
            pass
    return "0.0.0"


def write_app_version_to_json(app_path: Path, new_version: str) -> bool:
    """Schreibt neue app_version ins _custom JSON"""
    json_path = app_path / "_custom" / "config" / "app_config.json"
    if not json_path.exists():
        return False
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["app_version"] = new_version
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"   ⚠️  Fehler beim Schreiben der app_version: {e}")
        return False


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


def update_readme(app_path: Path, new_version: str) -> None:
    """Aktualisiert Last Update und Last Version im README"""
    readme = app_path / "README.md"
    if not readme.exists():
        return

    content = readme.read_text(encoding="utf-8")
    today = get_current_date()

    content = re.sub(
        r"(Last Update:\s*)[\d]{1,2}\.[\d]{1,2}\.[\d]{4}", f"\\g<1>{today}", content
    )
    content = re.sub(
        r"(Last Version:\s*)[\d]+\.[\d]+\.[\d]+", f"\\g<1>{new_version}", content
    )

    readme.write_text(content, encoding="utf-8")
    print(f"   📅 README: Last Update → {today}, Last Version → {new_version}")


# ========================================
# KERN: _BASE KOPIEREN & ANPASSEN
# ========================================


def replace_content(content: str, app_name: str) -> str:
    content = content.replace(TEMPLATE_NAME, app_name)
    content = re.sub(
        rf'AppLogger\("APP-{app_name}"\)',
        f'AppLogger("APP-{app_name.upper()}")',
        content,
    )
    return content


def copy_and_adapt_base(template_base: Path, target_base: Path, app_name: str) -> int:
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

    # PASS 2: Ordner sammeln
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

    # 1. Aktuelle app_version lesen (VOR dem Update)
    old_version = read_app_version_from_json(app_path)
    new_version = increment_version(old_version)
    print(f"   📦 app_version: {old_version} → {new_version}")

    # 2. Backup
    backup_path = app_path / "_base_backup"
    if backup_path.exists():
        shutil.rmtree(backup_path)
    if target_base.exists():
        shutil.copytree(target_base, backup_path)
        print(f"   💾 Backup erstellt: _base_backup/")

    # 3. Altes _base/ löschen
    if target_base.exists():
        shutil.rmtree(target_base)

    # 4. Neues _base/ kopieren und anpassen
    try:
        file_count = copy_and_adapt_base(template_base, target_base, app_name)
        print(f"   📁 _base/ aktualisiert ({file_count} Dateien)")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        if backup_path.exists():
            shutil.copytree(backup_path, target_base)
            print(f"   🔄 Rollback durchgeführt")
        return False

    # 5. app_version im JSON erhöhen
    if write_app_version_to_json(app_path, new_version):
        print(f"   ✓ app_version im JSON gesetzt: {new_version}")
    else:
        print(f"   ⚠️  app_version konnte nicht ins JSON geschrieben werden")

    # 6. README aktualisieren (Last Update + Last Version)
    update_readme(app_path, new_version)

    # 7. Backup entfernen
    if backup_path.exists():
        shutil.rmtree(backup_path)
        print(f"   🗑️  Backup entfernt")

    return True


# ========================================
# SCAN
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

    base_version = read_base_version_from_template(template_path)

    print("=" * 60)
    print("🔄  Flask App Update Script")
    print(f"    Template:      {TEMPLATE_NAME}")
    print(f"    admin_version: {base_version}  (aus _BASE_VERSION)")
    print(f"    app_version:   +0.0.1 pro App  (individuell)")
    print(f"    Filter:        Template_Base: {REQUIRED_BASE}")
    print("=" * 60)

    if not apps_path.exists():
        print(f"❌ apps/ Ordner nicht gefunden: {apps_path}")
        return
    if not template_path.exists():
        print(f"❌ Template nicht gefunden: {template_path}")
        return

    print(f"\n🔍 Scanne apps/ ...")
    candidates = scan_apps(apps_path)

    if not candidates:
        print(f"\n   Keine Apps mit Template_Base: {REQUIRED_BASE} gefunden.")
        return

    print(f"\n📋 Gefundene Apps ({len(candidates)}):")
    for app_path, app_name in candidates:
        current = read_app_version_from_json(app_path)
        print(
            f"   • {app_name:<30} app_version: {current} → {increment_version(current)}"
        )

    print(f"\n{'─' * 60}")
    print(f"⚠️  Folgendes wird überschrieben:")
    print(f"   - _base/ komplett (admin_version: {base_version})")
    print(f"   - app_version im JSON um 0.0.1 erhöht")
    print(f"   - README: Last Update + Last Version")
    print(f"\n   Nicht verändert: _custom/, models.py, __init__.py")
    print(f"{'─' * 60}")

    confirm = input("\nUpdate starten? (j/n): ").strip().lower()
    if confirm not in ["j", "ja", "y", "yes"]:
        print("⏹️  Abgebrochen.")
        return

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

    print(f"\n{'=' * 60}")
    print(f"📊 Zusammenfassung:")
    print(f"   ✅ Erfolgreich: {success_count}/{len(candidates)}")
    if failed:
        print(f"   ❌ Fehlgeschlagen: {', '.join(failed)}")
    print(f"\n💡 Nächster Schritt: Apps neu starten")
    print(f"   → AppConfig synct admin_app_version ins JSON")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
