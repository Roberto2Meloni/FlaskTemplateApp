from flask import jsonify, request
from flask_login import current_user
from app.decorators import enabled_required
from ... import blueprint, app_logger, app_config
from ...models import PrintlyPrinter, PrintlyFilament
from app import db

app_logger.info(f"Starte CUSTOM API Routes für {app_config.app_name}")

# ----------------------------------------------------------
# ERSTELLEN - Drucker
# ----------------------------------------------------------


@blueprint.route("/api/printers", methods=["POST"])
@enabled_required
def api_create_printer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    # Validierung
    if (
        not data.get("name")
        or not data.get("brand")
        or not data.get("machine_cost_per_hour")
    ):
        return jsonify({"error": "Name, Marke und Kosten sind Pflichtfelder"}), 422

    new_printer = PrintlyPrinter(
        name=data["name"],
        brand=data["brand"],
        machine_cost_per_hour=data["machine_cost_per_hour"],
        energy_consumption=data.get("energy_consumption"),
        notes=data.get("notes"),
        created_by=current_user.username,
    )
    db.session.add(new_printer)
    db.session.commit()

    return jsonify({"success": True, "printer": new_printer.to_dict()}), 201


@blueprint.route("/api/printers/<int:printer_id>", methods=["PUT"])
@enabled_required
def api_update_printer(printer_id):
    printer = PrintlyPrinter.query.get_or_404(printer_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    printer.name = data.get("name", printer.name)
    printer.brand = data.get("brand", printer.brand)
    printer.machine_cost_per_hour = data.get(
        "machine_cost_per_hour", printer.machine_cost_per_hour
    )
    printer.energy_consumption = data.get(
        "energy_consumption", printer.energy_consumption
    )
    printer.notes = data.get("notes", printer.notes)
    db.session.commit()

    return jsonify({"success": True, "printer": printer.to_dict()})


@blueprint.route("/api/printers/<int:printer_id>/archive", methods=["PUT"])
@enabled_required
def api_archive_printer(printer_id):
    printer = PrintlyPrinter.query.get_or_404(printer_id)
    printer.is_archived = not printer.is_archived  # Toggle
    db.session.commit()
    return jsonify({"success": True, "is_archived": printer.is_archived})


# ----------------------------------------------------------
# ERSTELLEN - Filamente
# ----------------------------------------------------------
@blueprint.route("/api/filaments", methods=["POST"])
@enabled_required
def api_create_filament():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    # Validierung
    required = ["filament_type", "name", "manufacturer", "weight", "price", "diameter"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Pflichtfelder fehlen: {', '.join(missing)}"}), 422

    new_filament = PrintlyFilament(
        filament_type=data["filament_type"],
        name=data["name"],
        color=data.get("color") or None,
        manufacturer=data["manufacturer"],
        diameter=float(data["diameter"]),
        weight=int(data["weight"]),
        price=float(data["price"]),
        notes=data.get("notes") or None,
        created_by=current_user.username,
    )
    db.session.add(new_filament)
    db.session.commit()

    app_logger.info(
        f"Filament '{new_filament.name}' erstellt von {current_user.username}"
    )
    return jsonify({"success": True, "filament": new_filament.to_dict()}), 201


# ----------------------------------------------------------
# BEARBEITEN
# ----------------------------------------------------------
@blueprint.route("/api/filaments/<int:filament_id>", methods=["PUT"])
@enabled_required
def api_update_filament(filament_id):
    filament = PrintlyFilament.query.get_or_404(filament_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    filament.filament_type = data.get("filament_type", filament.filament_type)
    filament.name = data.get("name", filament.name)
    filament.color = data.get("color") or filament.color
    filament.manufacturer = data.get("manufacturer", filament.manufacturer)
    filament.diameter = float(data.get("diameter", filament.diameter))
    filament.weight = int(data.get("weight", filament.weight))
    filament.price = float(data.get("price", filament.price))
    filament.notes = data.get("notes") or filament.notes
    db.session.commit()

    app_logger.info(
        f"Filament '{filament.name}' bearbeitet von {current_user.username}"
    )
    return jsonify({"success": True, "filament": filament.to_dict()})


# ----------------------------------------------------------
# ARCHIVIEREN (Friedhof Toggle)
# ----------------------------------------------------------
@blueprint.route("/api/filaments/<int:filament_id>/archive", methods=["PUT"])
@enabled_required
def api_archive_filament(filament_id):
    filament = PrintlyFilament.query.get_or_404(filament_id)
    filament.is_archived = not filament.is_archived
    db.session.commit()

    action = "begraben 🪦" if filament.is_archived else "wiederbelebt 💚"
    app_logger.info(f"Filament '{filament.name}' wurde {action}")
    return jsonify({"success": True, "is_archived": filament.is_archived})


app_logger.info(f"Ende CUSTOM API Routes für {app_config.app_name}")
