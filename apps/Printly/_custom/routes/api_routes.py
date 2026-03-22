from flask import jsonify, request
from flask_login import current_user
from app.decorators import enabled_required
from ... import blueprint, app_logger, app_config
from ...models import PrintlyPrinter
from app import db

app_logger.info(f"Starte CUSTOM API Routes für {app_config.app_name}")


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


app_logger.info(f"Ende CUSTOM API Routes für {app_config.app_name}")
