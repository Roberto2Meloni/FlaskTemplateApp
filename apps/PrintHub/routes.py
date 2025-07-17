from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    jsonify,
    current_app,
)
from flask_login import login_required, current_user
from app.decorators import enabled_required
from app.config import Config
from app import db, app
from .models import PrintHubFilament, get_current_time, PrintHubPrinter
from sqlalchemy.exc import IntegrityError


# Blueprint
blueprint = Blueprint(
    "PrintHub",
    __name__,
    url_prefix="/printhub",
    static_folder="static",
    template_folder="templates",
)

config = Config()


@blueprint.route("/printHub_index", methods=["GET"])
@enabled_required
# nur hier ist der Name gross!!
def PrintHub_index():
    app.logger.info("PrintHub page accessed")
    return render_template("PrintHub.html", user=current_user, config=config)


@blueprint.route("/printHub_filaments", methods=["GET", "POST"])
@login_required
@enabled_required
def printHub_filaments():
    """Filament-Verwaltung - Anzeigen und Hinzufügen"""

    if request.method == "POST":
        try:
            # Form-Daten extrahieren
            filament_type = request.form.get("filament_type", "").strip()
            name = request.form.get("filament_name", "").strip()
            manufacturer = request.form.get("filament_manufacturer", "").strip()
            weight = request.form.get("filament_weight", type=int)
            price = request.form.get("filament_price", type=float)
            notes = request.form.get("filament_notes", "").strip()

            # Validierung
            if not all([filament_type, name, manufacturer]) or not weight or not price:
                flash("Bitte füllen Sie alle Pflichtfelder aus!", "error")
                return redirect(url_for("PrintHub.printHub_filaments"))

            if weight <= 0 or price <= 0:
                flash("Gewicht und Preis müssen größer als 0 sein!", "error")
                return redirect(url_for("PrintHub.printHub_filaments"))

            if filament_type not in PrintHubFilament.get_filament_types():
                flash("Ungültiger Filament-Typ!", "error")
                return redirect(url_for("PrintHub.printHub_filaments"))

            # Neues Filament erstellen
            new_filament = PrintHubFilament(
                filament_type=filament_type,
                name=name,
                manufacturer=manufacturer,
                weight=weight,
                price=price,
                notes=notes if notes else None,
                created_by=current_user.username,
                created_at=get_current_time(),
                updated_at=get_current_time(),
            )

            # In Datenbank speichern
            db.session.add(new_filament)
            db.session.commit()

            flash(f'Filament "{name}" erfolgreich hinzugefügt!', "success")
            current_app.logger.info(
                f"User {current_user.username} added filament: {name}"
            )

        except IntegrityError as e:
            db.session.rollback()
            flash(
                "Fehler beim Speichern des Filaments. Bitte versuchen Sie es erneut.",
                "error",
            )
            current_app.logger.error(f"Database integrity error: {e}")

        except Exception as e:
            db.session.rollback()
            flash("Ein unerwarteter Fehler ist aufgetreten.", "error")
            current_app.logger.error(f"Unexpected error adding filament: {e}")

        return redirect(url_for("PrintHub.printHub_filaments"))

    # GET Request - Filamente laden
    try:
        # Suchparameter
        search_term = request.args.get("search", "").strip()
        filter_type = request.args.get("type", "").strip()

        # Filamente laden
        if search_term or filter_type:
            filaments = PrintHubFilament.search(
                username=current_user.username,
                search_term=search_term if search_term else None,
                filament_type=filter_type if filter_type else None,
            )
        else:
            filaments = PrintHubFilament.get_by_user(current_user.username)

        # Statistiken berechnen
        stats = {
            "total_filaments": len(filaments),
            "total_value": sum(float(f.price) for f in filaments),
            "total_weight": sum(f.weight for f in filaments),
            "types": {},
        }

        # Typ-Statistiken
        for filament in filaments:
            if filament.filament_type not in stats["types"]:
                stats["types"][filament.filament_type] = {
                    "count": 0,
                    "weight": 0,
                    "value": 0,
                }
            stats["types"][filament.filament_type]["count"] += 1
            stats["types"][filament.filament_type]["weight"] += filament.weight
            stats["types"][filament.filament_type]["value"] += float(filament.price)

        return render_template(
            "PrintHubFilaments.html",
            user=current_user,
            config=config,
            active_page="filaments",
            filaments=filaments,
            stats=stats,
            filament_types=PrintHubFilament.get_filament_types(),
            search_term=search_term,
            filter_type=filter_type,
        )

    except Exception as e:
        flash("Fehler beim Laden der Filamente.", "error")
        current_app.logger.error(f"Error loading filaments: {e}")
        return render_template(
            "PrintHubFilaments.html",
            user=current_user,
            config=config,
            active_page="filaments",
            filaments=[],
            stats={
                "total_filaments": 0,
                "total_value": 0,
                "total_weight": 0,
                "types": {},
            },
            filament_types=PrintHubFilament.get_filament_types(),
            search_term="",
            filter_type="",
        )


@blueprint.route("/filament/delete_filament/<int:filament_id>", methods=["POST"])
@enabled_required
def delete_filament(filament_id):
    """Filament löschen - nur eigene Filamente"""
    try:
        # Filament laden und prüfen ob es dem aktuellen Benutzer gehört
        filament = PrintHubFilament.query.filter_by(
            id=filament_id, created_by=current_user.username
        ).first()

        if not filament:
            flash(
                "Filament nicht gefunden oder Sie haben keine Berechtigung zum Löschen.",
                "error",
            )
            return redirect(url_for("PrintHub.printHub_filaments"))

        filament_name = filament.name
        filament_type = filament.filament_type

        # Filament löschen
        db.session.delete(filament)
        db.session.commit()

        flash(
            f'Filament "{filament_name}" ({filament_type}) erfolgreich gelöscht!',
            "success",
        )
        current_app.logger.info(
            f"User {current_user.username} deleted filament: {filament_name} ({filament_type})"
        )

    except Exception as e:
        db.session.rollback()
        flash("Fehler beim Löschen des Filaments.", "error")
        current_app.logger.error(f"Error deleting filament: {e}")

    return redirect(url_for("PrintHub.printHub_filaments"))


# API Endpoints
@blueprint.route("/api/filaments", methods=["GET"])
@enabled_required
def api_filaments():
    """API: Alle Filamente als JSON"""
    try:
        filaments = PrintHubFilament.get_by_user(current_user.username)
        return jsonify({"success": True, "data": [f.to_dict() for f in filaments]})
    except Exception as e:
        current_app.logger.error(f"Error in API filaments: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Printer Seiten
@blueprint.route("/printHub_printers", methods=["GET", "POST"])
@enabled_required
def printHub_printers():
    """Drucker-Verwaltung - Ohne manuelle Rollbacks"""

    if request.method == "POST":
        try:
            # Form-Daten extrahieren
            name = request.form.get("printer_name", "").strip()
            brand = request.form.get("printer_brand", "").strip()
            machine_cost_per_hour = request.form.get(
                "machine_cost_per_hour", type=float
            )
            energy_consumption = request.form.get("energy_consumption", type=int)
            notes = request.form.get("printer_notes", "").strip()

            # Validierung
            if not all([name, brand]) or not machine_cost_per_hour:
                flash("Bitte füllen Sie alle Pflichtfelder aus!", "error")
                return redirect(url_for("PrintHub.printHub_printers"))

            if machine_cost_per_hour <= 0:
                flash("Maschinenkosten müssen größer als 0 sein!", "error")
                return redirect(url_for("PrintHub.printHub_printers"))

            # Neuen Drucker erstellen
            new_printer = PrintHubPrinter(
                name=name,
                brand=brand,
                machine_cost_per_hour=machine_cost_per_hour,
                energy_consumption=energy_consumption if energy_consumption else None,
                notes=notes if notes else None,
                created_by=current_user.username,
            )

            db.session.add(new_printer)
            print("Printer added to reset session")
            db.session.commit()
            print("Reset session commit successful!")

            flash(f'Drucker "{name}" erfolgreich hinzugefügt!', "success")
            current_app.logger.info(
                f"User {current_user.username} added printer: {name}"
            )

        except Exception as e:
            flash("Ein unerwarteter Fehler ist aufgetreten.", "error")
            current_app.logger.error(f"Error with reset session: {e}")
            print(f"Error with reset session: {e}")

        return redirect(url_for("PrintHub.printHub_printers"))

    # GET Request - Drucker laden
    try:
        search_term = request.args.get("search", "").strip()

        if search_term:
            printers = PrintHubPrinter.search(
                username=current_user.username, search_term=search_term
            )
        else:
            printers = PrintHubPrinter.get_by_user(current_user.username)

        stats = {
            "total_printers": len(printers),
            "total_daily_cost": sum(p.daily_machine_cost for p in printers),
            "total_hourly_cost": sum(float(p.machine_cost_per_hour) for p in printers),
        }

        return render_template(
            "PrintHubPrinters.html",
            user=current_user,
            config=config,
            active_page="printers",
            printers=printers,
            stats=stats,
            printer_brands=PrintHubPrinter.get_common_brands(),
            search_term=search_term,
        )

    except Exception as e:
        flash("Fehler beim Laden der Drucker.", "error")
        current_app.logger.error(f"Error loading printers: {e}")
        return render_template(
            "PrintHubPrinters.html",
            user=current_user,
            config=config,
            active_page="printers",
            printers=[],
            stats={"total_printers": 0, "total_daily_cost": 0, "total_hourly_cost": 0},
            printer_brands=PrintHubPrinter.get_common_brands(),
            search_term="",
        )


@blueprint.route("/printer/delete_printer/<int:printer_id>", methods=["POST"])
@enabled_required
def delete_printer(printer_id):
    """Drucker löschen - nur eigene Drucker"""
    try:
        # Drucker laden und prüfen ob er dem aktuellen Benutzer gehört
        printer = PrintHubPrinter.query.filter_by(
            id=printer_id, created_by=current_user.username
        ).first()

        if not printer:
            flash(
                "Drucker nicht gefunden oder Sie haben keine Berechtigung zum Löschen.",
                "error",
            )
            return redirect(url_for("PrintHub.printHub_printers"))

        printer_name = printer.name
        printer_brand = printer.brand

        # Drucker löschen
        db.session.delete(printer)
        db.session.commit()

        flash(
            f'Drucker "{printer_name}" ({printer_brand}) erfolgreich gelöscht!',
            "success",
        )
        current_app.logger.info(
            f"User {current_user.username} deleted printer: {printer_name} ({printer_brand})"
        )

    except Exception as e:
        db.session.rollback()
        flash("Fehler beim Löschen des Druckers.", "error")
        current_app.logger.error(f"Error deleting printer: {e}")

    return redirect(url_for("PrintHub.printHub_printers"))


# API Endpoints
@blueprint.route("/api/printers", methods=["GET"])
@login_required
@enabled_required
def api_printers():
    """API: Alle Drucker als JSON"""
    try:
        printers = PrintHubPrinter.get_by_user(current_user.username)
        return jsonify({"success": True, "data": [p.to_dict() for p in printers]})
    except Exception as e:
        current_app.logger.error(f"Error in API printers: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
