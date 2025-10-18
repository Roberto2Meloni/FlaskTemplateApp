import mimetypes
import os
import base64
import uuid
import shutil
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

app_logger.info("Starte App-Template_app_v001 API")
config = Config()


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

    print(f"Path parts: {path_parts}")
    print(f"Root folder: '{root_folder}'")

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
            print("Kein Sub-Pfad")

        print(f"Full target path: '{full_target_path}'")

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

            return (
                jsonify(
                    {
                        "status": "success",
                        "message": "Bild erfolgreich hochgeladen",
                        "filename": unique_filename,
                    }
                ),
                200,
            )

        except Exception as e:
            # Fehler beim Speichern oder Verarbeiten des Bildes
            print(f"Fehler beim Bildupload: {e}")

            # Temporäre Datei löschen, falls vorhanden
            if os.path.exists(temp_path):
                os.remove(temp_path)

            return (
                jsonify({"status": "error", "message": "Fehler beim Bildupload"}),
                500,
            )

    except Exception as e:
        # Allgemeiner Fehler
        print(f"Unerwarteter Fehler: {e}")
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

        print(data)

        # Backends Pfad ermitteln
        backend_path = real_path(frontend_path)
        print(f"Backend-Pfad: {backend_path}")

        # Überprüfen, ob die Datei existiert
        if not os.path.exists(backend_path):
            return jsonify({"status": "error", "message": "Bild nicht gefunden"}), 404

        # Bild in Base64 kodieren
        with open(backend_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        mime_type = mimetypes.guess_type(backend_path)[0] or "image/jpeg"

        # Zusätzliche Bildinformationen sammeln
        image_info = {
            "status": "success",
            "filename": image_name,
            "path": frontend_path,
            "image": f"data:{mime_type};base64,{base64_image}",
            "size": os.path.getsize(backend_path),
            "last_modified": os.path.getmtime(backend_path),
        }
        return jsonify(image_info), 200

    except Exception as e:
        print(f"Fehler beim Laden des Bildes: {e}")
        return (
            jsonify({"status": "error", "message": "Fehler beim Laden des Bildes"}),
            500,
        )


@blueprint.route("/delete_image", methods=["POST"])
@enabled_required
def delete_image():
    try:
        # JSON-Daten aus der Anfrage extrahieren
        data = request.get_json()
        frontend_path = data.get("current_path")
        image_name = data.get("filename")

        print(data)

        # Backends Pfad ermitteln
        backend_path = real_path(frontend_path)
        print(f"Backend-Pfad: {backend_path}")

        # Überprüfen, ob die Datei existiert
        if not os.path.exists(backend_path):
            return jsonify({"status": "error", "message": "Bild nicht gefunden"}), 404

        # Löschen
        try:
            os.remove(backend_path)
            message = f"Bild {image_name} gelöscht"
            status = "success"
        except Exception as e:
            app_logger.error(f"Fehler beim Löschen des Bildes: {e}")
            message = f"Fehler beim Löschen des Bildes: {e}"
            status = "error"
        finally:
            return jsonify({"status": status, "message": message}), 200

    except Exception as e:
        print(f"Fehler beim Laden des Bildes: {e}")
        return (
            jsonify({"status": "error", "message": "Fehler beim Laden des Bildes"}),
            500,
        )


app_logger.info("Ende App-Template_app_v001 API")
