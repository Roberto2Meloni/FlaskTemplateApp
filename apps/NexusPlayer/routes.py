import os
from flask import render_template, current_app as app, request, jsonify
from flask_login import current_user
from . import blueprint, app_logger
from app.config import Config
from app.decorators import admin_required, enabled_required
from app import db
from .helper_app_functions.helper_app_functions import get_both, map_folder


# for Debuging
from icecream import ic

# from .models import xx
# from app.admin.models import User@
# from app.helper_functions.helper_db_file import check_if_user_has_admin_rights

config = Config()
app_logger.info("Starte App-NexusPlayer Route Initialization")
print("NexusPlayer Version 0.0.0")


@blueprint.route("/NexusPlayer_index", methods=["GET"])
@enabled_required
def NexusPlayer_index():
    return render_template("NexusPlayer.html", user=current_user, config=config)


@blueprint.route("/nexus_dashboard", methods=["GET"])
@enabled_required
def nexus_dashboard():
    return render_template("Nexus_Dashboard.html", user=current_user, config=config)


# Alles zum Theeme Files


@blueprint.route("/nexus_files", methods=["GET"])
@enabled_required
def nexus_files():
    full_architecture, simpel_architecture = get_both()
    return render_template(
        "Nexus_Files.html",
        user=current_user,
        config=config,
        full_architecture=full_architecture,
        simpel_architecture=simpel_architecture,
    )


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


@blueprint.route("/nexus_playlists", methods=["GET"])
@enabled_required
def nexus_playlists():
    return render_template("Nexus_Playlists.html", user=current_user, config=config)


@blueprint.route("/nexus_devices", methods=["GET"])
@enabled_required
def nexus_devices():
    return render_template("Nexus_Devices.html", user=current_user, config=config)


@blueprint.route("/nexus_admin", methods=["GET"])
@enabled_required
def nexus_admin():
    return render_template("Nexus_Admin.html", user=current_user, config=config)


app_logger.info("Ende App-NexusPlayer Route Initialization")
