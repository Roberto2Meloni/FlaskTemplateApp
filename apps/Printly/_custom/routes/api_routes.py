from flask import jsonify, request
from flask_login import current_user
from app.decorators import enabled_required
from ... import blueprint, app_logger, app_config
from datetime import date
from ...models import PrintlyPrinter, PrintlyFilament, PrintlyElectricityCost
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


# ----------------------------------------------------------
# ERSTELLEN - EnergyCost
# ----------------------------------------------------------
@blueprint.route("/api/energy_costs", methods=["POST"])
@enabled_required
def api_create_energy_cost():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    required = ["name", "provider", "cost_per_kwh"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Pflichtfelder fehlen: {', '.join(missing)}"}), 422

    new_cost = PrintlyElectricityCost(
        name=data["name"],
        provider=data["provider"],
        cost_per_kwh=float(data["cost_per_kwh"]),
        base_fee_monthly=(
            float(data["base_fee_monthly"]) if data.get("base_fee_monthly") else None
        ),
        tariff_type=data.get("tariff_type") or None,
        valid_from=(
            date.fromisoformat(data["valid_from"]) if data.get("valid_from") else None
        ),
        valid_until=(
            date.fromisoformat(data["valid_until"]) if data.get("valid_until") else None
        ),
        night_rate=float(data["night_rate"]) if data.get("night_rate") else None,
        is_active=data.get("is_active", True),
        notes=data.get("notes") or None,
        created_by=current_user.username,
    )
    db.session.add(new_cost)
    db.session.commit()

    app_logger.info(
        f"EnergyCost '{new_cost.name}' erstellt von {current_user.username}"
    )
    return jsonify({"success": True, "energy_cost": new_cost.to_dict()}), 201


# ----------------------------------------------------------
# BEARBEITEN
# ----------------------------------------------------------
@blueprint.route("/api/energy_costs/<int:cost_id>", methods=["PUT"])
@enabled_required
def api_update_energy_cost(cost_id):
    cost = PrintlyElectricityCost.query.get_or_404(cost_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    cost.name = data.get("name", cost.name)
    cost.provider = data.get("provider", cost.provider)
    cost.cost_per_kwh = float(data.get("cost_per_kwh", cost.cost_per_kwh))
    cost.base_fee_monthly = (
        float(data["base_fee_monthly"]) if data.get("base_fee_monthly") else None
    )
    cost.tariff_type = data.get("tariff_type") or cost.tariff_type
    cost.valid_from = (
        date.fromisoformat(data["valid_from"])
        if data.get("valid_from")
        else cost.valid_from
    )
    cost.valid_until = (
        date.fromisoformat(data["valid_until"])
        if data.get("valid_until")
        else cost.valid_until
    )
    cost.night_rate = float(data["night_rate"]) if data.get("night_rate") else None
    cost.is_active = data.get("is_active", cost.is_active)
    cost.notes = data.get("notes") or cost.notes
    db.session.commit()

    app_logger.info(f"EnergyCost '{cost.name}' bearbeitet von {current_user.username}")
    return jsonify({"success": True, "energy_cost": cost.to_dict()})


# ----------------------------------------------------------
# AKTIVIEREN / DEAKTIVIEREN (Toggle)
# ----------------------------------------------------------
@blueprint.route("/api/energy_costs/<int:cost_id>/toggle", methods=["PUT"])
@enabled_required
def api_toggle_energy_cost(cost_id):
    cost = PrintlyElectricityCost.query.get_or_404(cost_id)
    cost.is_active = not cost.is_active
    db.session.commit()

    status = "aktiviert" if cost.is_active else "deaktiviert"
    app_logger.info(f"EnergyCost '{cost.name}' wurde {status}")
    return jsonify({"success": True, "is_active": cost.is_active})


@blueprint.route("/api/energy_costs/<int:cost_id>", methods=["DELETE"])
@enabled_required
def api_delete_energy_cost(cost_id):
    cost = PrintlyElectricityCost.query.get_or_404(cost_id)
    name = cost.name
    db.session.delete(cost)
    db.session.commit()
    app_logger.info(f"ElectricityCost '{name}' gelöscht von {current_user.username}")
    return jsonify({"success": True})


app_logger.info(f"Ende CUSTOM API Routes für {app_config.app_name}")
