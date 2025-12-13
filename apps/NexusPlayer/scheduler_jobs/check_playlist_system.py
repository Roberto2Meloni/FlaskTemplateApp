import os
import json
import uuid
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app import db
from ..helper_app_functions.helper_app_functions import map_folder
from ..models import NexusPlayerPlaylists
from .. import app_logger


def check_playlist_system():
    """
    Hauptfunktion zur Synchronisation der Playlists
    """
    app_logger.info("Start check_playlist_system")
    try:
        check_and_sync_playlists()
        app_logger.info("Ende check_playlist_system")
    except Exception as e:
        app_logger.critical(f"Kritischer Fehler in check_playlist_system: {str(e)}")


def check_and_sync_playlists():
    """
    Synchronisiert Playlist-Dateien zwischen Dateisystem und Datenbank:
    - Löscht nicht-JSON Dateien
    - Validiert JSON-Struktur
    - Fügt UUID hinzu falls fehlt
    - Synchronisiert mit Datenbank
    """
    app_logger.info("Starte check_and_sync_playlists")

    try:
        # Hole den Pfad für Playlists
        playlist_path = map_folder.get("/Playlists")
        if not playlist_path or not os.path.exists(playlist_path):
            app_logger.error(f"Playlist-Verzeichnis nicht gefunden: {playlist_path}")
            return

        # Statistiken
        stats = {
            "total_files": 0,
            "valid_playlists": 0,
            "added_playlists": 0,
            "updated_playlists": 0,
            "deleted_playlists": 0,
            "deleted_invalid_files": 0,
            "fixed_uuids": 0,
            "errors": 0,
        }

        # Hole alle existierenden Playlists aus der DB (mit 'name' statt 'playlist_name')
        existing_playlists = {p.name: p for p in NexusPlayerPlaylists.query.all()}

        # Set für gefundene Playlists im Dateisystem
        found_playlists = set()

        # Durchsuche Playlist-Verzeichnis (nur root-level, nicht rekursiv)
        for filename in os.listdir(playlist_path):
            file_path = os.path.join(playlist_path, filename)

            # Überspringe Verzeichnisse
            if os.path.isdir(file_path):
                continue

            stats["total_files"] += 1

            # Prüfe ob es eine JSON-Datei ist
            if not filename.endswith(".json"):
                # Lösche nicht-JSON Dateien
                try:
                    os.remove(file_path)
                    app_logger.critical(
                        f"Ungültige Datei im Playlist-Ordner gelöscht: {filename}"
                    )
                    stats["deleted_invalid_files"] += 1
                except OSError as e:
                    app_logger.critical(
                        f"Fehler beim Löschen der ungültigen Datei {filename}: {str(e)}"
                    )
                    stats["errors"] += 1
                continue

            # Verarbeite JSON-Playlist
            result = process_playlist_file(
                file_path, filename, existing_playlists, stats
            )

            if result:
                playlist_name = result.get("playlist_name")
                if playlist_name:
                    found_playlists.add(playlist_name)
                    stats["valid_playlists"] += 1

        # Entferne Playlists aus DB, die nicht mehr im Dateisystem existieren
        stats["deleted_playlists"] = remove_deleted_playlists(
            existing_playlists, found_playlists
        )

        # Commit aller Änderungen
        db.session.commit()

        # Logging der Statistiken
        log_playlist_statistics(stats)

    except SQLAlchemyError as db_error:
        db.session.rollback()
        app_logger.critical(f"Datenbankfehler bei Playlist-Sync: {str(db_error)}")
        raise
    except Exception as e:
        db.session.rollback()
        app_logger.critical(f"Unerwarteter Fehler bei Playlist-Sync: {str(e)}")
        raise

    app_logger.info("Ende check_and_sync_playlists")


def process_playlist_file(file_path, filename, existing_playlists, stats):
    """
    Verarbeitet eine einzelne Playlist-JSON-Datei

    Returns:
        dict: Playlist-Daten oder None bei Fehler
    """
    try:
        # Lade JSON-Datei
        with open(file_path, "r", encoding="utf-8") as f:
            playlist_data = json.load(f)

        # Validiere erforderliche Felder
        required_fields = [
            "playlist_name",
            "created_at",
            "created_by",
            "last_modified",
            "last_modified_by",
            "count_elements",
            "elements",
            "description",
        ]

        missing_fields = [
            field for field in required_fields if field not in playlist_data
        ]

        if missing_fields:
            app_logger.error(
                f"Playlist {filename} hat fehlende Felder: {', '.join(missing_fields)}"
            )
            stats["errors"] += 1
            return None

        playlist_name = playlist_data["playlist_name"]

        # Prüfe, ob Dateiname mit playlist_name übereinstimmt
        expected_filename = f"{playlist_name}.json"
        if filename != expected_filename:
            app_logger.warning(
                f"Dateiname '{filename}' stimmt nicht mit playlist_name "
                f"'{playlist_name}' überein. Erwartet: '{expected_filename}'"
            )

        # Prüfe und füge UUID hinzu falls fehlt
        file_modified = False
        if not playlist_data.get("playlist_uuid"):
            playlist_data["playlist_uuid"] = str(uuid.uuid4())
            file_modified = True
            stats["fixed_uuids"] += 1
            app_logger.info(f"UUID für Playlist '{playlist_name}' erstellt")

        # Speichere Datei falls modifiziert
        if file_modified:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(playlist_data, f, indent=2, ensure_ascii=False)
            app_logger.info(f"Playlist-Datei '{filename}' aktualisiert")

        # Synchronisiere mit Datenbank
        sync_playlist_to_db(playlist_data, existing_playlists, stats)

        return playlist_data

    except json.JSONDecodeError as e:
        app_logger.critical(f"Ungültiges JSON-Format in {filename}: {str(e)}")
        stats["errors"] += 1
        return None
    except OSError as e:
        app_logger.error(f"Dateifehler bei {filename}: {str(e)}")
        stats["errors"] += 1
        return None
    except Exception as e:
        app_logger.error(f"Fehler beim Verarbeiten von {filename}: {str(e)}")
        stats["errors"] += 1
        return None


def sync_playlist_to_db(playlist_data, existing_playlists, stats):
    """
    Synchronisiert Playlist-Daten mit der Datenbank
    """
    try:
        playlist_name = playlist_data["playlist_name"]
        db_playlist = existing_playlists.get(playlist_name)

        # Konvertiere Datumsstrings zu datetime (falls nötig)
        created_at = parse_date(playlist_data["created_at"])
        last_modified = parse_date(playlist_data["last_modified"])

        # Konvertiere created_by zu Integer falls es ein String ist
        created_by = playlist_data["created_by"]
        if isinstance(created_by, str):
            if created_by.lower() == "system":
                created_by = 0
            else:
                try:
                    created_by = int(created_by)
                except ValueError:
                    created_by = 0  # Fallback

        if db_playlist:
            # Prüfe ob Aktualisierung nötig ist
            needs_update = (
                db_playlist.playlist_uuid != playlist_data["playlist_uuid"]
                or db_playlist.last_modified != last_modified
                or db_playlist.count_elements != playlist_data["count_elements"]
                or db_playlist.description != playlist_data["description"]
            )

            if needs_update:
                # Aktualisiere existierende Playlist
                db_playlist.playlist_uuid = playlist_data["playlist_uuid"]
                db_playlist.last_modified = last_modified
                db_playlist.last_modified_by = playlist_data["last_modified_by"]
                db_playlist.count_elements = playlist_data["count_elements"]
                db_playlist.description = playlist_data["description"]

                app_logger.info(f"Playlist in DB aktualisiert: {playlist_name}")
                stats["updated_playlists"] += 1
        else:
            # Erstelle neue Playlist in DB
            new_playlist = NexusPlayerPlaylists(
                playlist_uuid=playlist_data["playlist_uuid"],
                name=playlist_name,  # ← 'name' statt 'playlist_name'
                created_at=created_at,
                created_by=created_by,  # ← Integer (User ID)
                last_modified=last_modified,
                last_modified_by=playlist_data["last_modified_by"],
                count_elements=playlist_data["count_elements"],
                description=playlist_data["description"],
            )

            db.session.add(new_playlist)
            app_logger.info(f"Neue Playlist in DB hinzugefügt: {playlist_name}")
            stats["added_playlists"] += 1

    except Exception as e:
        app_logger.error(
            f"Fehler beim Synchronisieren von Playlist '{playlist_name}' mit DB: {str(e)}"
        )
        stats["errors"] += 1


def remove_deleted_playlists(existing_playlists, found_playlists):
    """
    Entfernt Playlists aus der Datenbank, die nicht mehr im Dateisystem existieren

    Args:
        existing_playlists: Dictionary der DB-Playlists {name: playlist_object}
        found_playlists: Set der gefundenen Playlist-Namen

    Returns:
        int: Anzahl der gelöschten Einträge
    """
    deleted_count = 0

    for playlist_name, db_playlist in existing_playlists.items():
        if playlist_name not in found_playlists:
            try:
                db.session.delete(db_playlist)
                app_logger.info(
                    f"Playlist aus DB entfernt (nicht mehr im Dateisystem): {playlist_name}"
                )
                deleted_count += 1
            except SQLAlchemyError as e:
                app_logger.error(
                    f"Fehler beim Löschen von Playlist '{playlist_name}': {str(e)}"
                )

    return deleted_count


def parse_date(date_string):
    """
    Konvertiert Datumsstring zu datetime-Objekt
    Unterstützt Format: DD.MM.YYYY

    Returns:
        datetime: Parsed datetime oder aktuelles Datum bei Fehler
    """
    try:
        # Format: 18.10.2025
        return datetime.strptime(date_string, "%d.%m.%Y")
    except (ValueError, TypeError):
        # Fallback: aktuelles Datum
        app_logger.warning(
            f"Ungültiges Datumsformat: {date_string}, verwende aktuelles Datum"
        )
        return datetime.now()


def log_playlist_statistics(stats):
    """Loggt die Statistiken der Playlist-Synchronisation"""
    app_logger.info("Playlist-Synchronisation abgeschlossen")
    app_logger.info(f"Gesamte Dateien gescannt: {stats['total_files']}")
    app_logger.info(f"Gültige Playlists: {stats['valid_playlists']}")
    app_logger.info(f"Neue Playlists hinzugefügt: {stats['added_playlists']}")
    app_logger.info(f"Playlists aktualisiert: {stats['updated_playlists']}")
    app_logger.info(f"Playlists aus DB gelöscht: {stats['deleted_playlists']}")
    app_logger.info(f"Ungültige Dateien gelöscht: {stats['deleted_invalid_files']}")
    app_logger.info(f"Fehlende UUIDs ergänzt: {stats['fixed_uuids']}")
    app_logger.info(f"Fehler: {stats['errors']}")
