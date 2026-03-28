from flask import jsonify, request
from flask_login import current_user
from app.decorators import enabled_required
from ... import blueprint, app_logger, app_config
from datetime import date
from ...models import (
    PrintlyPrinter,
    PrintlyFilament,
    PrintlyElectricityCost,
    PrintlyWorkHours,
    PrintlyOverheadProfile,
    printly_printer_overhead,
    PrintlyDiscountProfile,
)
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


@blueprint.route("/api/work_hours", methods=["POST"])
@enabled_required
def api_create_work_hours():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    if not data.get("name") or not data.get("cost_per_hour"):
        return jsonify({"error": "Name und Stundensatz sind Pflichtfelder"}), 422

    new_rate = PrintlyWorkHours(
        name=data["name"],
        cost_per_hour=float(data["cost_per_hour"]),
        notes=data.get("notes") or None,
        created_by=current_user.username,
    )
    db.session.add(new_rate)
    db.session.commit()

    app_logger.info(f"WorkHours '{new_rate.name}' erstellt von {current_user.username}")
    return jsonify({"success": True, "work_hours": new_rate.to_dict()}), 201


@blueprint.route("/api/work_hours/<int:rate_id>", methods=["PUT"])
@enabled_required
def api_update_work_hours(rate_id):
    rate = PrintlyWorkHours.query.get_or_404(rate_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    rate.name = data.get("name", rate.name)
    rate.cost_per_hour = float(data.get("cost_per_hour", rate.cost_per_hour))
    rate.notes = data.get("notes") or None
    db.session.commit()

    app_logger.info(f"WorkHours '{rate.name}' bearbeitet von {current_user.username}")
    return jsonify({"success": True, "work_hours": rate.to_dict()})


@blueprint.route("/api/work_hours/<int:rate_id>/archive", methods=["PUT"])
@enabled_required
def api_archive_work_hours(rate_id):
    rate = PrintlyWorkHours.query.get_or_404(rate_id)
    rate.is_archived = not rate.is_archived
    db.session.commit()

    action = "begraben 🪦" if rate.is_archived else "wiederbelebt 💚"
    app_logger.info(f"WorkHours '{rate.name}' wurde {action}")
    return jsonify({"success": True, "is_archived": rate.is_archived})


@blueprint.route("/api/work_hours/<int:rate_id>", methods=["DELETE"])
@enabled_required
def api_delete_work_hours(rate_id):
    rate = PrintlyWorkHours.query.get_or_404(rate_id)
    name = rate.name
    db.session.delete(rate)
    db.session.commit()

    app_logger.info(f"WorkHours '{name}' gelöscht von {current_user.username}")
    return jsonify({"success": True})


# ----------------------------------------------------------
# ERSTELLEN - Overhead Profile
# ----------------------------------------------------------
@blueprint.route("/api/overhead_profiles", methods=["POST"])
@enabled_required
def api_create_overhead_profile():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    if not data.get("name"):
        return jsonify({"error": "Name ist Pflichtfeld"}), 422

    profile = PrintlyOverheadProfile(
        name=data["name"],
        location=data.get("location") or None,
        rent_monthly=float(data.get("rent_monthly") or 0),
        electricity_monthly=float(data.get("electricity_monthly") or 0),
        insurance=float(data.get("insurance") or 0),
        internet=float(data.get("internet") or 0),
        software_cost=float(data.get("software_cost") or 0),
        software_billing=data.get("software_billing", "monthly"),
        other_costs=float(data.get("other_costs") or 0),
        planned_hours_monthly=int(data.get("planned_hours_monthly") or 100),
        is_active=data.get("is_active", True),
        notes=data.get("notes") or None,
        created_by=current_user.username,
    )
    db.session.add(profile)
    db.session.commit()

    app_logger.info(
        f"OverheadProfile '{profile.name}' erstellt von {current_user.username}"
    )
    return jsonify({"success": True, "profile": profile.to_dict()}), 201


# ----------------------------------------------------------
# BEARBEITEN
# ----------------------------------------------------------
@blueprint.route("/api/overhead_profiles/<int:profile_id>", methods=["PUT"])
@enabled_required
def api_update_overhead_profile(profile_id):
    profile = PrintlyOverheadProfile.query.get_or_404(profile_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    profile.name = data.get("name", profile.name)
    profile.location = data.get("location") or profile.location
    profile.rent_monthly = float(data.get("rent_monthly") or 0)
    profile.electricity_monthly = float(data.get("electricity_monthly") or 0)
    profile.insurance = float(data.get("insurance") or 0)
    profile.internet = float(data.get("internet") or 0)
    profile.software_cost = float(data.get("software_cost") or 0)
    profile.software_billing = data.get("software_billing", profile.software_billing)
    profile.other_costs = float(data.get("other_costs") or 0)
    profile.planned_hours_monthly = int(
        data.get("planned_hours_monthly") or profile.planned_hours_monthly
    )
    profile.is_active = data.get("is_active", profile.is_active)
    profile.notes = data.get("notes") or None
    db.session.commit()

    app_logger.info(
        f"OverheadProfile '{profile.name}' bearbeitet von {current_user.username}"
    )
    return jsonify({"success": True, "profile": profile.to_dict()})


# ----------------------------------------------------------
# TOGGLE AKTIV/INAKTIV
# ----------------------------------------------------------
@blueprint.route("/api/overhead_profiles/<int:profile_id>/toggle", methods=["PUT"])
@enabled_required
def api_toggle_overhead_profile(profile_id):
    profile = PrintlyOverheadProfile.query.get_or_404(profile_id)
    profile.is_active = not profile.is_active
    db.session.commit()

    status = "aktiviert" if profile.is_active else "deaktiviert"
    app_logger.info(f"OverheadProfile '{profile.name}' wurde {status}")
    return jsonify({"success": True, "is_active": profile.is_active})


# ----------------------------------------------------------
# LÖSCHEN
# ----------------------------------------------------------
@blueprint.route("/api/overhead_profiles/<int:profile_id>", methods=["DELETE"])
@enabled_required
def api_delete_overhead_profile(profile_id):
    profile = PrintlyOverheadProfile.query.get_or_404(profile_id)
    name = profile.name
    db.session.delete(profile)
    db.session.commit()

    app_logger.info(f"OverheadProfile '{name}' gelöscht von {current_user.username}")
    return jsonify({"success": True})


# ----------------------------------------------------------
# VERKNÜPFUNG: Drucker ↔ Overhead (Schritt 2)
# ----------------------------------------------------------
@blueprint.route(
    "/api/overhead_profiles/<int:profile_id>/link_printer", methods=["POST"]
)
@enabled_required
def api_link_printer_to_overhead(profile_id):
    profile = PrintlyOverheadProfile.query.get_or_404(profile_id)
    data = request.get_json()
    printer_id = data.get("printer_id")
    is_default = data.get("is_default", False)

    printer = PrintlyPrinter.query.get_or_404(printer_id)

    # Prüfen ob Verknüpfung bereits existiert
    existing = db.session.execute(
        db.select(printly_printer_overhead).where(
            printly_printer_overhead.c.printer_id == printer_id,
            printly_printer_overhead.c.overhead_id == profile_id,
        )
    ).fetchone()

    if existing:
        return jsonify({"error": "Verknüpfung existiert bereits"}), 409

    # Falls is_default → alle anderen auf False setzen
    if is_default:
        db.session.execute(
            printly_printer_overhead.update()
            .where(printly_printer_overhead.c.printer_id == printer_id)
            .values(is_default=False)
        )

    db.session.execute(
        printly_printer_overhead.insert().values(
            printer_id=printer_id,
            overhead_id=profile_id,
            is_default=is_default,
        )
    )
    db.session.commit()

    app_logger.info(f"Drucker '{printer.name}' mit Overhead '{profile.name}' verknüpft")
    return jsonify({"success": True})


@blueprint.route(
    "/api/overhead_profiles/<int:profile_id>/unlink_printer", methods=["DELETE"]
)
@enabled_required
def api_unlink_printer_from_overhead(profile_id):
    data = request.get_json()
    printer_id = data.get("printer_id")

    db.session.execute(
        printly_printer_overhead.delete().where(
            printly_printer_overhead.c.printer_id == printer_id,
            printly_printer_overhead.c.overhead_id == profile_id,
        )
    )
    db.session.commit()

    app_logger.info(
        f"Verknüpfung Drucker {printer_id} ↔ Overhead {profile_id} entfernt"
    )
    return jsonify({"success": True})


# ----------------------------------------------------------
# ERSTELLEN - Discount Profile
# ----------------------------------------------------------


@blueprint.route("/api/discount_profiles", methods=["POST"])
@enabled_required
def api_create_discount_profile():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    if not data.get("name") or data.get("percentage") is None:
        return jsonify({"error": "Name und Prozentsatz sind Pflichtfelder"}), 422

    profile = PrintlyDiscountProfile(
        name=data["name"],
        discount_type=data.get("discount_type", "discount"),
        percentage=float(data["percentage"]),
        notes=data.get("notes") or None,
        is_active=data.get("is_active", True),
        created_by=current_user.username,
    )
    db.session.add(profile)
    db.session.commit()

    app_logger.info(
        f"DiscountProfile '{profile.name}' erstellt von {current_user.username}"
    )
    return jsonify({"success": True, "profile": profile.to_dict()}), 201


@blueprint.route("/api/discount_profiles/<int:profile_id>", methods=["PUT"])
@enabled_required
def api_update_discount_profile(profile_id):
    profile = PrintlyDiscountProfile.query.get_or_404(profile_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    profile.name = data.get("name", profile.name)
    profile.discount_type = data.get("discount_type", profile.discount_type)
    profile.percentage = float(data.get("percentage", profile.percentage))
    profile.notes = data.get("notes") or None
    profile.is_active = data.get("is_active", profile.is_active)
    db.session.commit()

    app_logger.info(
        f"DiscountProfile '{profile.name}' bearbeitet von {current_user.username}"
    )
    return jsonify({"success": True, "profile": profile.to_dict()})


@blueprint.route("/api/discount_profiles/<int:profile_id>/toggle", methods=["PUT"])
@enabled_required
def api_toggle_discount_profile(profile_id):
    profile = PrintlyDiscountProfile.query.get_or_404(profile_id)
    profile.is_active = not profile.is_active
    db.session.commit()

    status = "aktiviert" if profile.is_active else "deaktiviert"
    app_logger.info(f"DiscountProfile '{profile.name}' wurde {status}")
    return jsonify({"success": True, "is_active": profile.is_active})


@blueprint.route("/api/discount_profiles/<int:profile_id>", methods=["DELETE"])
@enabled_required
def api_delete_discount_profile(profile_id):
    profile = PrintlyDiscountProfile.query.get_or_404(profile_id)
    name = profile.name
    db.session.delete(profile)
    db.session.commit()

    app_logger.info(f"DiscountProfile '{name}' gelöscht von {current_user.username}")
    return jsonify({"success": True})


app_logger.info(f"Ende CUSTOM API Routes für {app_config.app_name}")
