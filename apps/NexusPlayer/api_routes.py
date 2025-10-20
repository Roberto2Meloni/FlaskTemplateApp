from datetime import datetime
import mimetypes
import os
import base64
import uuid
import shutil
import imghdr
from werkzeug.utils import secure_filename
from . import blueprint, app_logger
from app.decorators import admin_required, enabled_required
from flask_login import current_user
from app.config import Config
from flask import request, jsonify
from .helper_app_functions.helper_app_functions import (
    map_folder,
    is_valid_image,
    real_path,
    generate_unique_filename,
)
from .models import NexusPlayerFiles
from app import db
from sqlalchemy.exc import SQLAlchemyError
from .app_config import AppConfig


config = Config()
app_config = AppConfig()
app_logger.info(f"Starte App-{app_config.app_name} API")


@blueprint.route("/create_new_folder", methods=["POST"])
@enabled_required
def create_new_folder():
    data = request.get_json()
    new_folder_name = data["new_folder_name"]
    current_path_origin = data["current_path"]

    print(f"Original Pfad: '{current_path_origin}'")

    # Schritt 1: Root-Ordner aus dem Pfad extrahieren
    path_parts = current_path_origin.strip("/").split("/")
    root_folder = f"/{path_parts[0]}" if path_parts[0] else "/"

    if root_folder in map_folder:
        real_root_path = map_folder[root_folder]
        print(f"Real root path: '{real_root_path}'")

        # Schritt 2: Unterordner-Pfad erstellen (falls vorhanden)
        if len(path_parts) > 1:
            sub_path = "/".join(path_parts[1:])
            full_target_path = os.path.join(real_root_path, sub_path)
            print(f"Sub path: '{sub_path}'")
        else:
            full_target_path = real_root_path
        #     print("Kein Sub-Pfad")

        # print(f"Full target path: '{full_target_path}'")

        if os.path.exists(full_target_path):
            new_folder_full_path = os.path.join(full_target_path, new_folder_name)
            print(f"Neuer Ordner Pfad: '{new_folder_full_path}'")

            if os.path.exists(new_folder_full_path):
                return jsonify(success=False, message="Der Ordner existiert bereits")
            else:
                try:
                    os.makedirs(new_folder_full_path)
                    return jsonify(
                        success=True,
                        message=f"Der Ordner wurde erstellt in: {new_folder_full_path}",
                    )
                except Exception as e:
                    print(f"Fehler beim Erstellen: {e}")
                    return jsonify(success=False, message=str(e))
        else:
            print(f"Zielpfad existiert nicht: '{full_target_path}'")
            return jsonify(
                success=False,
                message=f"Der Zielpfad existiert nicht: {full_target_path}",
            )
    else:
        print(f"Root-Ordner nicht gefunden: '{root_folder}'")
        return jsonify(success=False, message="Ungültiger Root-Ordner")


@blueprint.route("/upload_image", methods=["POST"])
@enabled_required
def upload_image():
    try:
        # JSON-Daten aus der Anfrage extrahieren
        data = request.get_json()

        # Pfad aus den Daten extrahieren
        frontend_path = data.get("current_path")
        backend_path = real_path(frontend_path)
        image_base64 = data.get("image")
        original_filename = data.get("filename")

        # Validierung der Eingabedaten
        if not backend_path or not image_base64 or not original_filename:
            return (
                jsonify(
                    {"status": "error", "message": "Fehlende Bilddaten oder Zielpfad"}
                ),
                400,
            )

        # Temporären Ordner direkt aus map_folder holen
        temp_folder = map_folder.get("/Temp")

        # Eindeutigen Dateinamen generieren
        unique_filename = generate_unique_filename(backend_path, original_filename)

        # Vollständiger temporärer Pfad
        temp_path = os.path.join(temp_folder, unique_filename)
        ziel_dateipfad = os.path.join(backend_path, unique_filename)

        try:
            # Base64-Daten dekodieren und speichern
            with open(temp_path, "wb") as datei:
                # Sicherstellen, dass nur der Base64-Teil dekodiert wird
                base64_data = image_base64.split(",")[-1]
                datei.write(base64.b64decode(base64_data))

            # Bild validieren
            if not is_valid_image(temp_path):
                # Ungültige Bilddatei löschen
                os.remove(temp_path)
                return (
                    jsonify({"status": "error", "message": "Ungültiges Bildformat"}),
                    400,
                )

            # Stelle sicher, dass der Zielordner existiert
            os.makedirs(os.path.dirname(ziel_dateipfad), exist_ok=True)

            # Bild in den Zielordner kopieren
            shutil.copy2(temp_path, ziel_dateipfad)

            # Temporäre Datei löschen
            os.remove(temp_path)

            # ==========================================
            # NEU: Datei in Datenbank eintragen
            # ==========================================
            try:
                # Hole Datei-Metadaten
                file_stats = os.stat(ziel_dateipfad)

                # Bestimme den Bildtyp
                image_type = imghdr.what(ziel_dateipfad)
                if not image_type:
                    # Fallback auf Dateiendung
                    image_type = unique_filename.rsplit(".", 1)[-1].lower()

                # Berechne relativen Pfad zum Inhaltsverzeichnis
                content_path = map_folder.get("/Inhalte")
                relative_path = os.path.relpath(ziel_dateipfad, content_path)

                # Prüfe, ob Datei bereits existiert (Sicherheitscheck)
                existing_file = NexusPlayerFiles.query.filter_by(
                    name=unique_filename, path=relative_path
                ).first()

                if existing_file:
                    # Aktualisiere existierenden Eintrag
                    existing_file.size = file_stats.st_size
                    existing_file.last_modified = datetime.fromtimestamp(
                        file_stats.st_mtime
                    )
                    existing_file.last_modified_by = (
                        current_user.id if current_user.is_authenticated else "System"
                    )
                    existing_file.type = image_type

                    app_logger.info(f"Datei in DB aktualisiert: {unique_filename}")
                    db_action = "updated"
                else:
                    # Erstelle neuen Datenbank-Eintrag
                    new_file = NexusPlayerFiles(
                        file_uuid=str(uuid.uuid4()),
                        name=unique_filename,
                        path=relative_path,
                        type=image_type,
                        size=file_stats.st_size,
                        last_modified=datetime.fromtimestamp(file_stats.st_mtime),
                        created_at=datetime.now(),
                        created_by=(
                            current_user.id if current_user.is_authenticated else 1
                        ),
                        last_modified_by=(
                            current_user.id
                            if current_user.is_authenticated
                            else "System"
                        ),
                    )

                    db.session.add(new_file)
                    app_logger.info(f"Neue Datei in DB erstellt: {unique_filename}")
                    db_action = "created"

                # Commit der DB-Änderungen
                db.session.commit()

                return (
                    jsonify(
                        {
                            "status": "success",
                            "message": "Bild erfolgreich hochgeladen",
                            "filename": unique_filename,
                            "db_action": db_action,
                            "file_uuid": (
                                existing_file.file_uuid
                                if existing_file
                                else new_file.file_uuid
                            ),
                        }
                    ),
                    200,
                )

            except SQLAlchemyError as db_error:
                # Rollback bei DB-Fehler
                db.session.rollback()
                app_logger.error(
                    f"DB-Fehler beim Upload von {unique_filename}: {str(db_error)}"
                )

                # Datei wurde hochgeladen, aber DB-Eintrag fehlgeschlagen
                return (
                    jsonify(
                        {
                            "status": "warning",
                            "message": "Bild hochgeladen, aber Datenbank-Eintrag fehlgeschlagen",
                            "filename": unique_filename,
                            "db_error": str(db_error),
                        }
                    ),
                    201,  # 201 Created, aber mit Warnung
                )

        except Exception as e:
            # Fehler beim Speichern oder Verarbeiten des Bildes
            app_logger.error(f"Fehler beim Bildupload: {e}")

            # Temporäre Datei löschen, falls vorhanden
            if os.path.exists(temp_path):
                os.remove(temp_path)

            # Zieldatei löschen, falls erstellt wurde
            if os.path.exists(ziel_dateipfad):
                os.remove(ziel_dateipfad)

            return (
                jsonify(
                    {"status": "error", "message": f"Fehler beim Bildupload: {str(e)}"}
                ),
                500,
            )

    except Exception as e:
        # Allgemeiner Fehler
        app_logger.error(f"Unerwarteter Fehler beim Upload: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Ein unerwarteter Fehler ist aufgetreten",
                }
            ),
            500,
        )


@blueprint.route("/show_image", methods=["POST"])
@enabled_required
def show_image():
    try:
        # JSON-Daten aus der Anfrage extrahieren
        data = request.get_json()
        frontend_path = data.get("current_path")
        image_name = data.get("filename")

        app_logger.debug(f"show_image request data: {data}")

        # Backends Pfad ermitteln
        backend_path = real_path(frontend_path)
        app_logger.debug(f"Backend-Pfad: {backend_path}")

        # Überprüfen, ob die Datei existiert
        if not os.path.exists(backend_path):
            return jsonify({"status": "error", "message": "Bild nicht gefunden"}), 404

        # ==========================================
        # NEU: Datei-Informationen aus DB holen
        # ==========================================
        content_path = map_folder.get("/Inhalte")
        relative_path = os.path.relpath(backend_path, content_path)

        # Suche Datei in der Datenbank
        db_file = NexusPlayerFiles.query.filter_by(
            name=image_name, path=relative_path
        ).first()

        # DB-Informationen vorbereiten
        db_info = None
        if db_file:
            # Verwende to_dict() Methode
            db_info = db_file.to_dict()

            # Konvertiere Datetime-Objekte zu ISO-Strings für JSON
            if db_info.get("created_at"):
                db_info["created_at"] = db_info["created_at"].isoformat()
            if db_info.get("last_modified"):
                db_info["last_modified"] = db_info["last_modified"].isoformat()

            app_logger.debug(f"DB-Eintrag gefunden für {image_name}")
        else:
            app_logger.warning(
                f"Kein DB-Eintrag gefunden für {image_name} (Pfad: {relative_path})"
            )

        # Bild in Base64 kodieren
        with open(backend_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        mime_type = mimetypes.guess_type(backend_path)[0] or "image/jpeg"

        # Dateisystem-Informationen
        file_stats = os.stat(backend_path)

        # Kombinierte Bildinformationen
        image_info = {
            "status": "success",
            "filename": image_name,
            "path": frontend_path,
            "relative_path": relative_path,
            "image": f"data:{mime_type};base64,{base64_image}",
            "mime_type": mime_type,
            # Dateisystem-Informationen
            "file_system": {
                "size": file_stats.st_size,
                "last_modified": file_stats.st_mtime,
                "created": file_stats.st_ctime,
            },
            # Datenbank-Informationen
            "database": db_info,
            # Status-Flag
            "in_database": db_info is not None,
        }

        return jsonify(image_info), 200

    except Exception as e:
        app_logger.error(f"Fehler beim Laden des Bildes: {e}")
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Fehler beim Laden des Bildes",
                    "error_detail": str(e),
                }
            ),
            500,
        )


@blueprint.route("/delete_image", methods=["POST"])
@enabled_required
def delete_image():
    try:
        # JSON-Daten aus der Anfrage extrahieren
        data = request.get_json()

        # Debug: Zeige was empfangen wurde
        app_logger.debug(f"Delete request data: {data}")

        frontend_path = data.get("current_path")
        image_name = data.get("filename")

        # Validierung
        if not frontend_path:
            return jsonify({"status": "error", "message": "Kein Pfad angegeben"}), 400

        # Extrahiere Dateinamen aus Pfad, falls nicht direkt angegeben
        if not image_name:
            image_name = os.path.basename(frontend_path)
            app_logger.debug(f"Dateiname aus Pfad extrahiert: {image_name}")

        if not image_name:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Kein Dateiname angegeben oder im Pfad gefunden",
                    }
                ),
                400,
            )

        app_logger.debug(f"Lösche Bild: {image_name}")

        # Backends Pfad ermitteln
        backend_path = real_path(frontend_path)
        app_logger.debug(f"Backend-Pfad: {backend_path}")

        # Überprüfen, ob die Datei existiert
        if not os.path.exists(backend_path):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Bild '{image_name}' nicht gefunden",
                    }
                ),
                404,
            )

        # Berechne relativen Pfad für DB-Lookup
        content_path = map_folder.get("/Inhalte")
        relative_path = os.path.relpath(backend_path, content_path)

        app_logger.debug(f"Suche DB-Eintrag: name={image_name}, path={relative_path}")

        # Suche DB-Eintrag
        db_file = NexusPlayerFiles.query.filter_by(
            name=image_name, path=relative_path
        ).first()

        if db_file:
            app_logger.debug(
                f"DB-Eintrag gefunden: ID={db_file.id}, UUID={db_file.file_uuid}"
            )
        else:
            app_logger.debug(
                f"Kein DB-Eintrag gefunden für name={image_name}, path={relative_path}"
            )

        # Lösche Datei aus Dateisystem
        try:
            os.remove(backend_path)
            app_logger.info(f"Datei aus Dateisystem gelöscht: {image_name}")
            file_deleted = True
        except OSError as e:
            app_logger.error(f"Fehler beim Löschen der Datei aus dem Dateisystem: {e}")
            file_deleted = False
            error_message = str(e)

        # Lösche DB-Eintrag (falls vorhanden)
        db_deleted = False
        db_error = None

        if db_file:
            try:
                db.session.delete(db_file)
                db.session.commit()
                app_logger.info(f"DB-Eintrag gelöscht: {image_name} (ID: {db_file.id})")
                db_deleted = True
            except SQLAlchemyError as db_err:
                db.session.rollback()
                app_logger.error(f"Fehler beim Löschen des DB-Eintrags: {db_err}")
                db_error = str(db_err)
        else:
            app_logger.warning(
                f"Kein DB-Eintrag gefunden für {image_name} (Pfad: {relative_path})"
            )

        # Bestimme Response-Status
        if file_deleted and (db_deleted or not db_file):
            # Erfolg: Datei gelöscht und DB aktualisiert (oder kein DB-Eintrag vorhanden)
            return (
                jsonify(
                    {
                        "status": "success",
                        "message": f"Bild '{image_name}' erfolgreich gelöscht",
                        "file_deleted": True,
                        "db_deleted": db_deleted,
                        "had_db_entry": db_file is not None,
                    }
                ),
                200,
            )

        elif file_deleted and not db_deleted:
            # Teilweiser Erfolg: Datei gelöscht, aber DB-Fehler
            return (
                jsonify(
                    {
                        "status": "warning",
                        "message": f"Datei '{image_name}' gelöscht, aber DB-Eintrag konnte nicht entfernt werden",
                        "file_deleted": True,
                        "db_deleted": False,
                        "db_error": db_error,
                    }
                ),
                200,
            )

        else:
            # Fehler: Datei konnte nicht gelöscht werden
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": f"Fehler beim Löschen von '{image_name}': {error_message}",
                        "file_deleted": False,
                        "db_deleted": False,
                    }
                ),
                500,
            )

    except Exception as e:
        app_logger.error(f"Unerwarteter Fehler beim Löschen des Bildes: {e}")
        import traceback

        app_logger.error(traceback.format_exc())
        return (
            jsonify(
                {
                    "status": "error",
                    "message": f"Unerwarteter Fehler beim Löschen: {str(e)}",
                }
            ),
            500,
        )


app_logger.info(f"Ende App-{app_config.app_name} API")
