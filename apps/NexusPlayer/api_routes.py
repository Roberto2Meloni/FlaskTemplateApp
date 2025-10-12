import os
from . import blueprint, app_logger
from app.decorators import admin_required, enabled_required
from flask_login import current_user
from app.config import Config
from flask import request, jsonify
from .helper_app_functions.helper_app_functions import map_folder

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


app_logger.info("Ende App-Template_app_v001 API")
