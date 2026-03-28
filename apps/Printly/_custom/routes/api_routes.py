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
    PrintlyCompany,
    PrintlyCustomer,
    generate_company_number,
    generate_customer_number,
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

    linked_companies = PrintlyCompany.query.filter_by(
        discount_profile_id=profile_id
    ).all()
    linked_customers = PrintlyCustomer.query.filter_by(
        discount_profile_id=profile_id
    ).all()

    if linked_companies or linked_customers:
        details = []
        for c in linked_companies:
            details.append(f"🏢 {c.company_name} ({c.company_number})")
        for c in linked_customers:
            details.append(f"👤 {c.full_name} ({c.customer_number})")

        return (
            jsonify(
                {"success": False, "error": "Rabatt noch verknüpft", "linked": details}
            ),
            409,
        )

    name = profile.name
    db.session.delete(profile)
    db.session.commit()
    app_logger.info(f"DiscountProfile '{name}' gelöscht")
    return jsonify({"success": True})


# ============================================================
# FIRMEN
# ============================================================


@blueprint.route("/api/companies", methods=["POST"])
@enabled_required
def api_create_company():
    data = request.get_json()
    if not data or not data.get("company_name"):
        return jsonify({"error": "Firmenname ist Pflichtfeld"}), 422

    try:
        # Firmennummer inline berechnen
        last = PrintlyCompany.query.order_by(PrintlyCompany.id.desc()).first()
        next_id = (last.id + 1) if last else 1
        company_number = f"F-{next_id:04d}"

        company = PrintlyCompany(
            company_number=company_number,
            company_name=data["company_name"],
            email=data.get("email") or None,
            phone=data.get("phone") or None,
            website=data.get("website") or None,
            address=data.get("address") or None,
            zip_code=data.get("zip_code") or None,
            city=data.get("city") or None,
            country=data.get("country", "CH"),
            discount_profile_id=data.get("discount_profile_id") or None,
            is_active=data.get("is_active", True),
            notes=data.get("notes") or None,
            created_by=current_user.username,
        )
        db.session.add(company)
        db.session.commit()

        app_logger.info(
            f"Company '{company.company_name}' ({company.company_number}) erstellt"
        )
        return jsonify({"success": True, "company": company.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        app_logger.error(f"Fehler Company erstellen: {e}")
        return jsonify({"error": str(e)}), 500


@blueprint.route("/api/companies/<int:company_id>", methods=["PUT"])
@enabled_required
def api_update_company(company_id):
    company = PrintlyCompany.query.get_or_404(company_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    company.company_name = data.get("company_name", company.company_name)
    company.email = data.get("email") or None
    company.phone = data.get("phone") or None
    company.website = data.get("website") or None
    company.address = data.get("address") or None
    company.zip_code = data.get("zip_code") or None
    company.city = data.get("city") or None
    company.country = data.get("country", company.country)
    company.discount_profile_id = data.get("discount_profile_id") or None
    company.is_active = data.get("is_active", company.is_active)
    company.notes = data.get("notes") or None
    db.session.commit()

    return jsonify({"success": True, "company": company.to_dict()})


@blueprint.route("/api/companies/<int:company_id>/toggle", methods=["PUT"])
@enabled_required
def api_toggle_company(company_id):
    company = PrintlyCompany.query.get_or_404(company_id)
    company.is_active = not company.is_active
    db.session.commit()
    return jsonify({"success": True, "is_active": company.is_active})


@blueprint.route("/api/companies/<int:company_id>", methods=["DELETE"])
@enabled_required
def api_delete_company(company_id):
    company = PrintlyCompany.query.get_or_404(company_id)
    name = company.company_name
    db.session.delete(company)
    db.session.commit()
    app_logger.info(f"Company '{name}' gelöscht")
    return jsonify({"success": True})


# ============================================================
# KUNDEN (Privat + Firmenkontakte)
# ============================================================


@blueprint.route("/api/customers", methods=["POST"])
@enabled_required
def api_create_customer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    if not data.get("first_name") or not data.get("last_name"):
        return jsonify({"error": "Vor- und Nachname sind Pflichtfelder"}), 422

    try:
        # Kundennummer direkt hier berechnen
        last = PrintlyCustomer.query.order_by(PrintlyCustomer.id.desc()).first()
        next_id = (last.id + 1) if last else 1
        customer_number = f"K-{next_id:04d}"

        company_id = data.get("company_id") or None
        if company_id and data.get("is_primary"):
            PrintlyCustomer.query.filter_by(
                company_id=company_id, is_primary=True
            ).update({"is_primary": False})

        customer = PrintlyCustomer(
            customer_number=customer_number,
            company_id=company_id,
            first_name=data["first_name"],
            last_name=data["last_name"],
            role=data.get("role") or None,
            is_primary=data.get("is_primary", False),
            email=data.get("email") or None,
            phone=data.get("phone") or None,
            address=data.get("address") or None,
            zip_code=data.get("zip_code") or None,
            city=data.get("city") or None,
            country=data.get("country", "CH"),
            discount_profile_id=data.get("discount_profile_id") or None,
            is_active=data.get("is_active", True),
            notes=data.get("notes") or None,
            created_by=current_user.username,
        )
        db.session.add(customer)
        db.session.flush()  # ← NEU: wirft den echten Fehler
        db.session.commit()

        return jsonify({"success": True, "customer": customer.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        import traceback

        tb = traceback.format_exc()
        app_logger.error(f"Fehler Customer erstellen: {tb}")
        print(tb)
        return jsonify({"error": tb}), 500


@blueprint.route("/api/customers/<int:customer_id>", methods=["PUT"])
@enabled_required
def api_update_customer(customer_id):
    customer = PrintlyCustomer.query.get_or_404(customer_id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Keine Daten"}), 400

    # is_primary → alle anderen in der Firma auf False
    if data.get("is_primary") and customer.company_id:
        PrintlyCustomer.query.filter(
            PrintlyCustomer.company_id == customer.company_id,
            PrintlyCustomer.id != customer_id,
        ).update({"is_primary": False})

    customer.first_name = data.get("first_name", customer.first_name)
    customer.last_name = data.get("last_name", customer.last_name)
    customer.role = data.get("role") or None
    customer.is_primary = data.get("is_primary", customer.is_primary)
    customer.email = data.get("email") or None
    customer.phone = data.get("phone") or None
    customer.address = data.get("address") or None
    customer.zip_code = data.get("zip_code") or None
    customer.city = data.get("city") or None
    customer.country = data.get("country", customer.country)
    customer.discount_profile_id = data.get("discount_profile_id") or None
    customer.is_active = data.get("is_active", customer.is_active)
    customer.notes = data.get("notes") or None
    db.session.commit()

    return jsonify({"success": True, "customer": customer.to_dict()})


@blueprint.route("/api/customers/<int:customer_id>/toggle", methods=["PUT"])
@enabled_required
def api_toggle_customer(customer_id):
    customer = PrintlyCustomer.query.get_or_404(customer_id)
    customer.is_active = not customer.is_activeF
    db.session.commit()
    return jsonify({"success": True, "is_active": customer.is_active})


@blueprint.route("/api/customers/<int:customer_id>", methods=["DELETE"])
@enabled_required
def api_delete_customer(customer_id):
    customer = PrintlyCustomer.query.get_or_404(customer_id)
    name = customer.full_name
    db.session.delete(customer)
    db.session.commit()
    app_logger.info(f"Customer '{name}' gelöscht")
    return jsonify({"success": True})


app_logger.info(f"Ende CUSTOM API Routes für {app_config.app_name}")
