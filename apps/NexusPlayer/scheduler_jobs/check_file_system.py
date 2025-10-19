import os
import uuid
import imghdr
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app import db
from ..helper_app_functions.helper_app_functions import map_folder
from ..models import NexusPlayerFiles
from .. import app_logger

# Erlaubte Bildformate
ERLAUBTE_FORMATE = {"png", "jpg", "jpeg", "gif", "bmp", "webp"}


def check_file_system():
    """
    Hauptfunktion zur Synchronisation des Dateisystems mit der Datenbank
    """
    app_logger.info("Start check_file_system")
    try:
        check_and_sync_files()
        app_logger.info("Ende check_file_system")
    except Exception as e:
        app_logger.critical(f"Kritischer Fehler in check_file_system: {str(e)}")


def check_and_sync_files():
    """
    Synchronisiert Dateien zwischen Dateisystem und Datenbank:
    - Fügt neue Dateien hinzu
    - Aktualisiert geänderte Dateien
    - Entfernt gelöschte Dateien aus der DB
    """
    app_logger.info("Starte check_and_sync_files")

    try:
        # Hole den Pfad für Inhalte
        content_path = map_folder.get("/Inhalte")
        if not content_path or not os.path.exists(content_path):
            app_logger.error(f"Inhaltsverzeichnis nicht gefunden: {content_path}")
            return

        # Statistiken
        stats = {
            "total_files": 0,
            "added_files": 0,
            "updated_files": 0,
            "deleted_files": 0,
            "skipped_files": 0,
            "non_image_files": 0,
        }

        # Hole alle existierenden Dateien aus der DB (als Dictionary für schnellen Zugriff)
        existing_files = {(f.name, f.path): f for f in NexusPlayerFiles.query.all()}

        # Set für gefundene Dateien im Dateisystem
        found_files = set()

        # Durchsuche alle Dateien im Inhaltsverzeichnis
        for root, _, files in os.walk(content_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, content_path)

                # Markiere Datei als gefunden
                found_files.add((filename, relative_path))

                # Verarbeite die Datei
                result = process_file(
                    file_path, filename, relative_path, existing_files, content_path
                )

                # Aktualisiere Statistiken
                stats["total_files"] += 1
                if result == "added":
                    stats["added_files"] += 1
                elif result == "updated":
                    stats["updated_files"] += 1
                elif result == "skipped_invalid":
                    stats["skipped_files"] += 1
                elif result == "non_image":
                    stats["non_image_files"] += 1

        # Entferne Dateien aus DB, die nicht mehr im Dateisystem existieren
        stats["deleted_files"] = remove_deleted_files(existing_files, found_files)

        # Commit aller Änderungen
        db.session.commit()

        # Logging der Statistiken
        log_statistics(stats)

    except SQLAlchemyError as db_error:
        db.session.rollback()
        app_logger.critical(f"Datenbankfehler: {str(db_error)}")
        raise
    except Exception as e:
        db.session.rollback()
        app_logger.critical(f"Unerwarteter Fehler: {str(e)}")
        raise

    app_logger.info("Ende check_and_sync_files")


def process_file(file_path, filename, relative_path, existing_files, content_path):
    """
    Verarbeitet eine einzelne Datei: Prüfung, Hinzufügen oder Aktualisierung

    Returns:
        str: Status der Verarbeitung ('added', 'updated', 'exists', 'skipped_invalid', 'non_image')
    """
    try:
        # Prüfe Dateiendung
        file_extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        # Keine Bilddatei - nur loggen
        if file_extension not in ERLAUBTE_FORMATE:
            app_logger.debug(
                f"Nicht-Bild-Datei gefunden: {filename} (wird später verarbeitet)"
            )
            return "non_image"

        # Überprüfe, ob es wirklich ein Bild ist
        image_type = imghdr.what(file_path)
        if not image_type or image_type not in ERLAUBTE_FORMATE:
            app_logger.warning(
                f"Ungültige Bilddatei (Format-Prüfung fehlgeschlagen): {filename}"
            )
            return "skipped_invalid"

        # Hole Datei-Metadaten
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        last_modified = datetime.fromtimestamp(file_stats.st_mtime)

        # Prüfe, ob Datei bereits in DB existiert
        db_file = existing_files.get((filename, relative_path))

        if db_file:
            # Prüfe, ob Aktualisierung nötig ist
            if (
                db_file.size != file_size
                or db_file.last_modified != last_modified
                or db_file.type != image_type
            ):

                # Aktualisiere Datei in DB
                db_file.size = file_size
                db_file.last_modified = last_modified
                db_file.type = image_type
                db_file.last_modified_by = "System"

                app_logger.info(f"Datei aktualisiert: {filename}")
                return "updated"

            return "exists"

        # Neue Datei - zur DB hinzufügen
        new_file = NexusPlayerFiles(
            file_uuid=str(uuid.uuid4()),
            name=filename,
            path=relative_path,
            type=image_type,
            size=file_size,
            last_modified=last_modified,
            created_at=datetime.now(),
            created_by=0,  # System
            last_modified_by="System",
        )

        db.session.add(new_file)
        app_logger.info(f"Neue Datei hinzugefügt: {filename}")
        return "added"

    except OSError as os_error:
        app_logger.error(f"Dateisystemfehler bei {filename}: {str(os_error)}")
        return "skipped_invalid"
    except SQLAlchemyError as db_error:
        app_logger.error(f"Datenbankfehler bei {filename}: {str(db_error)}")
        return "skipped_invalid"
    except Exception as e:
        app_logger.error(f"Unerwarteter Fehler bei {filename}: {str(e)}")
        return "skipped_invalid"


def remove_deleted_files(existing_files, found_files):
    """
    Entfernt Dateien aus der Datenbank, die nicht mehr im Dateisystem existieren

    Args:
        existing_files: Dictionary der DB-Dateien {(name, path): file_object}
        found_files: Set der gefundenen Dateien {(name, path)}

    Returns:
        int: Anzahl der gelöschten Einträge
    """
    deleted_count = 0

    for file_key, db_file in existing_files.items():
        if file_key not in found_files:
            try:
                db.session.delete(db_file)
                app_logger.info(
                    f"Datei aus DB entfernt (nicht mehr im Dateisystem): {db_file.name}"
                )
                deleted_count += 1
            except SQLAlchemyError as e:
                app_logger.error(f"Fehler beim Löschen von {db_file.name}: {str(e)}")

    return deleted_count


def log_statistics(stats):
    """Loggt die Statistiken der Dateisynchronisation"""
    app_logger.info(
        f"Dateisynchronisation abgeschlossen:\n"
        f"  - Gesamte Dateien gescannt: {stats['total_files']}\n"
        f"  - Neue Dateien hinzugefügt: {stats['added_files']}\n"
        f"  - Dateien aktualisiert: {stats['updated_files']}\n"
        f"  - Dateien aus DB gelöscht: {stats['deleted_files']}\n"
        f"  - Ungültige Dateien übersprungen: {stats['skipped_files']}\n"
        f"  - Nicht-Bild-Dateien: {stats['non_image_files']}"
    )
