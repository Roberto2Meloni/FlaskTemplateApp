from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    jsonify,
    current_app,
    send_file,
)
from . import blueprint, app_logger

from flask_login import login_required, current_user
from app.decorators import enabled_required
from app.config import Config
from app import db, app

from .models import (
    PrintHubFilament,
    get_current_time,
    PrintHubPrinter,
    PrintHubEnergyCost,
    PrintHubWorkHours,
    PrintHubOverheadProfile,
    PrintHubDiscountProfile,
    PrintHubQuote,
    PrintHubSubOrder,
)

from sqlalchemy.exc import IntegrityError
from datetime import datetime
import tempfile
import os
import csv
import io
import zipfile
from werkzeug.utils import secure_filename

config = Config()
app_logger.info("Starte App-PrintHub Route Initialization")
print("PrintHub Version 0.0.0")


# Erweiterte Dashboard Route (in routes.py ersetzen/erweitern)


@blueprint.route("/printHub_index", methods=["GET"])
@enabled_required
def PrintHub_index():
    """Dashboard mit Offerten-Übersicht"""
    app_logger.info("PrintHub page accessed")

    try:
        # Statistiken für Dashboard sammeln
        recent_quotes = []
        total_quote_value = 0
        printer_count = 0
        filament_count = 0

        if current_user.is_authenticated:
            # Letzte Offerten (letzten 30 Tage)
            from datetime import datetime, timedelta

            thirty_days_ago = datetime.now() - timedelta(days=30)

            recent_quotes = (
                PrintHubQuote.query.filter(
                    PrintHubQuote.created_by == current_user.username,
                    PrintHubQuote.created_at >= thirty_days_ago,
                    PrintHubQuote.is_archived == False,
                )
                .order_by(PrintHubQuote.created_at.desc())
                .limit(10)
                .all()
            )

            # Gesamtwert aller Offerten
            all_quotes = PrintHubQuote.query.filter_by(
                created_by=current_user.username, is_archived=False
            ).all()
            total_quote_value = sum(float(quote.total_cost) for quote in all_quotes)

            # Anzahl Drucker und Filamente
            printer_count = len(PrintHubPrinter.get_by_user(current_user.username))
            filament_count = len(PrintHubFilament.get_by_user(current_user.username))

        return render_template(
            "PrintHub.html",
            user=current_user,
            config=config,
            recent_quotes=recent_quotes,
            total_quote_value=total_quote_value,
            printer_count=printer_count,
            filament_count=filament_count,
        )

    except Exception as e:
        app_logger.error(f"Error loading dashboard: {e}")
        # Fallback für Fehlerfall
        return render_template(
            "PrintHub.html",
            user=current_user,
            config=config,
            recent_quotes=[],
            total_quote_value=0,
            printer_count=0,
            filament_count=0,
        )


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
            current_app_logger.info(
                f"User {current_user.username} added filament: {name}"
            )

        except IntegrityError as e:
            db.session.rollback()
            flash(
                "Fehler beim Speichern des Filaments. Bitte versuchen Sie es erneut.",
                "error",
            )
            current_app_logger.error(f"Database integrity error: {e}")

        except Exception as e:
            db.session.rollback()
            flash("Ein unerwarteter Fehler ist aufgetreten.", "error")
            current_app_logger.error(f"Unexpected error adding filament: {e}")

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
        current_app_logger.error(f"Error loading filaments: {e}")
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
        current_app_logger.info(
            f"User {current_user.username} deleted filament: {filament_name} ({filament_type})"
        )

    except Exception as e:
        db.session.rollback()
        flash("Fehler beim Löschen des Filaments.", "error")
        current_app_logger.error(f"Error deleting filament: {e}")

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
        current_app_logger.error(f"Error in API filaments: {e}")
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
            current_app_logger.info(
                f"User {current_user.username} added printer: {name}"
            )

        except Exception as e:
            flash("Ein unerwarteter Fehler ist aufgetreten.", "error")
            current_app_logger.error(f"Error with reset session: {e}")
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
        current_app_logger.error(f"Error loading printers: {e}")
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
        current_app_logger.info(
            f"User {current_user.username} deleted printer: {printer_name} ({printer_brand})"
        )

    except Exception as e:
        db.session.rollback()
        flash("Fehler beim Löschen des Druckers.", "error")
        current_app_logger.error(f"Error deleting printer: {e}")

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
        current_app_logger.error(f"Error in API printers: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Engergikosten
@blueprint.route("/printHub_energy_costs", methods=["GET", "POST"])
@enabled_required
def printHub_energy_costs():
    """Energiekosten-Verwaltung - Anzeigen und Hinzufügen"""

    if request.method == "POST":
        try:
            # Form-Daten extrahieren
            name = request.form.get("energy_name", "").strip()
            provider = request.form.get("energy_provider", "").strip()
            cost_per_kwh = request.form.get("cost_per_kwh", type=float)
            base_fee_monthly = request.form.get("base_fee_monthly", type=float)
            tariff_type = request.form.get("tariff_type", "").strip()
            valid_from = request.form.get("valid_from", "")
            valid_until = request.form.get("valid_until", "")
            night_rate = request.form.get("night_rate", type=float)
            is_active = request.form.get("is_active") == "on"
            notes = request.form.get("energy_notes", "").strip()

            # Validierung
            if not all([name, provider]) or not cost_per_kwh:
                flash("Bitte füllen Sie alle Pflichtfelder aus!", "error")
                return redirect(url_for("PrintHub.printHub_energy_costs"))

            if cost_per_kwh <= 0:
                flash("Kosten pro kWh müssen größer als 0 sein!", "error")
                return redirect(url_for("PrintHub.printHub_energy_costs"))

            if base_fee_monthly and base_fee_monthly < 0:
                flash("Grundgebühr kann nicht negativ sein!", "error")
                return redirect(url_for("PrintHub.printHub_energy_costs"))

            # Datum-Konvertierung
            valid_from_date = None
            valid_until_date = None

            if valid_from:
                try:
                    valid_from_date = datetime.strptime(valid_from, "%Y-%m-%d").date()
                except ValueError:
                    flash("Ungültiges 'Gültig von' Datum!", "error")
                    return redirect(url_for("PrintHub.printHub_energy_costs"))

            if valid_until:
                try:
                    valid_until_date = datetime.strptime(valid_until, "%Y-%m-%d").date()
                    if valid_from_date and valid_until_date <= valid_from_date:
                        flash("'Gültig bis' muss nach 'Gültig von' liegen!", "error")
                        return redirect(url_for("PrintHub.printHub_energy_costs"))
                except ValueError:
                    flash("Ungültiges 'Gültig bis' Datum!", "error")
                    return redirect(url_for("PrintHub.printHub_energy_costs"))

            # Neue Energiekosten erstellen
            new_energy_cost = PrintHubEnergyCost(
                name=name,
                provider=provider,
                cost_per_kwh=cost_per_kwh,
                base_fee_monthly=base_fee_monthly if base_fee_monthly else None,
                tariff_type=tariff_type if tariff_type else None,
                valid_from=valid_from_date,
                valid_until=valid_until_date,
                night_rate=night_rate if night_rate else None,
                is_active=is_active,
                notes=notes if notes else None,
                created_by=current_user.username,
                created_at=get_current_time(),
                updated_at=get_current_time(),
            )

            # In Datenbank speichern
            db.session.add(new_energy_cost)
            db.session.commit()

            flash(f'Energietarif "{name}" erfolgreich hinzugefügt!', "success")
            current_app_logger.info(
                f"User {current_user.username} added energy cost: {name}"
            )

        except Exception as e:
            flash("Ein unerwarteter Fehler ist aufgetreten.", "error")
            current_app_logger.error(f"Unexpected error adding energy cost: {e}")

        return redirect(url_for("PrintHub.printHub_energy_costs"))

    # GET Request - Energiekosten laden
    try:
        # Suchparameter
        search_term = request.args.get("search", "").strip()
        filter_provider = request.args.get("provider", "").strip()
        show_inactive = request.args.get("show_inactive", "").strip() == "true"

        # Energiekosten laden
        if search_term or filter_provider:
            energy_costs = PrintHubEnergyCost.search(
                username=current_user.username,
                search_term=search_term if search_term else None,
                provider=filter_provider if filter_provider else None,
                include_inactive=show_inactive,
            )
        else:
            energy_costs = PrintHubEnergyCost.get_by_user(
                current_user.username, include_inactive=show_inactive
            )

        # Statistiken berechnen
        active_costs = [ec for ec in energy_costs if ec.is_active]

        stats = {
            "total_tariffs": len(energy_costs),
            "active_tariffs": len(active_costs),
            "avg_cost_per_kwh": (
                sum(float(ec.cost_per_kwh) for ec in active_costs) / len(active_costs)
                if active_costs
                else 0
            ),
            "cheapest_tariff": min(
                active_costs, key=lambda x: x.cost_per_kwh, default=None
            ),
            "most_expensive_tariff": max(
                active_costs, key=lambda x: x.cost_per_kwh, default=None
            ),
            "providers": list(set(ec.provider for ec in energy_costs)),
            "total_monthly_base_fees": sum(
                float(ec.base_fee_monthly or 0) for ec in active_costs
            ),
        }

        return render_template(
            "PrintHubEnergyCosts.html",
            user=current_user,
            config=config,
            active_page="energy_costs",
            energy_costs=energy_costs,
            stats=stats,
            tariff_types=PrintHubEnergyCost.get_tariff_types(),
            providers=stats["providers"],
            search_term=search_term,
            filter_provider=filter_provider,
            show_inactive=show_inactive,
        )

    except Exception as e:
        flash("Fehler beim Laden der Energiekosten.", "error")
        current_app_logger.error(f"Error loading energy costs: {e}")
        return render_template(
            "PrintHubEnergyCosts.html",
            user=current_user,
            config=config,
            active_page="energy_costs",
            energy_costs=[],
            stats={
                "total_tariffs": 0,
                "active_tariffs": 0,
                "avg_cost_per_kwh": 0,
                "cheapest_tariff": None,
                "most_expensive_tariff": None,
                "providers": [],
                "total_monthly_base_fees": 0,
            },
            tariff_types=PrintHubEnergyCost.get_tariff_types(),
            providers=[],
            search_term="",
            filter_provider="",
            show_inactive=False,
        )


# Zu Ihrer routes.py hinzufügen:


@blueprint.route(
    "/energy_cost/delete_energy_cost/<int:energy_cost_id>", methods=["POST"]
)
@enabled_required
def delete_energy_cost(energy_cost_id):
    """Energiekosten löschen - nur eigene Energiekosten"""
    try:
        # Energiekosten laden und prüfen ob sie dem aktuellen Benutzer gehören
        energy_cost = PrintHubEnergyCost.query.filter_by(
            id=energy_cost_id, created_by=current_user.username
        ).first()

        if not energy_cost:
            flash(
                "Energietarif nicht gefunden oder Sie haben keine Berechtigung zum Löschen.",
                "error",
            )
            return redirect(url_for("PrintHub.printHub_energy_costs"))

        energy_cost_name = energy_cost.name
        energy_cost_provider = energy_cost.provider

        # Energiekosten löschen
        db.session.delete(energy_cost)
        db.session.commit()

        flash(
            f'Energietarif "{energy_cost_name}" ({energy_cost_provider}) erfolgreich gelöscht!',
            "success",
        )
        current_app_logger.info(
            f"User {current_user.username} deleted energy cost: {energy_cost_name} ({energy_cost_provider})"
        )

    except Exception as e:
        flash("Fehler beim Löschen des Energietarifs.", "error")
        current_app_logger.error(f"Error deleting energy cost: {e}")

    return redirect(url_for("PrintHub.printHub_energy_costs"))


# Zu Ihrer routes.py hinzufügen:


@blueprint.route("/printHub_work_hours", methods=["GET", "POST"])
@enabled_required
def printHub_work_hours():
    """Arbeitszeiten-Verwaltung - Anzeigen und Hinzufügen"""

    if request.method == "POST":
        try:
            # Form-Daten extrahieren
            name = request.form.get("worker_name", "").strip()
            role = request.form.get("worker_role", "").strip()
            cost_per_hour = request.form.get("cost_per_hour", type=float)

            # Validierung
            if not all([name, role]) or not cost_per_hour:
                flash("Bitte füllen Sie alle Pflichtfelder aus!", "error")
                return redirect(url_for("PrintHub.printHub_work_hours"))

            if cost_per_hour <= 0:
                flash("Kosten pro Stunde müssen größer als 0 sein!", "error")
                return redirect(url_for("PrintHub.printHub_work_hours"))

            # Neue Arbeitszeit erstellen
            new_work_hour = PrintHubWorkHours(
                name=name,
                role=role,
                cost_per_hour=cost_per_hour,
                created_by=current_user.username,
                created_at=get_current_time(),
                updated_at=get_current_time(),
            )

            # In Datenbank speichern
            db.session.add(new_work_hour)
            db.session.commit()

            flash(f'Arbeitszeit für "{name}" erfolgreich hinzugefügt!', "success")
            current_app_logger.info(
                f"User {current_user.username} added work hour: {name}"
            )

        except Exception as e:
            flash("Ein unerwarteter Fehler ist aufgetreten.", "error")
            current_app_logger.error(f"Unexpected error adding work hour: {e}")

        return redirect(url_for("PrintHub.printHub_work_hours"))

    # GET Request - Arbeitszeiten laden
    try:
        # Suchparameter
        search_term = request.args.get("search", "").strip()
        filter_role = request.args.get("role", "").strip()

        # Arbeitszeiten laden
        if search_term or filter_role:
            work_hours = PrintHubWorkHours.search(
                username=current_user.username,
                search_term=search_term if search_term else None,
                role=filter_role if filter_role else None,
            )
        else:
            work_hours = PrintHubWorkHours.get_by_user(current_user.username)

        # Statistiken berechnen
        stats = {
            "total_workers": len(work_hours),
            "avg_cost_per_hour": (
                sum(float(wh.cost_per_hour) for wh in work_hours) / len(work_hours)
                if work_hours
                else 0
            ),
            "cheapest_worker": min(
                work_hours, key=lambda x: x.cost_per_hour, default=None
            ),
            "most_expensive_worker": max(
                work_hours, key=lambda x: x.cost_per_hour, default=None
            ),
            "roles": list(set(wh.role for wh in work_hours if wh.role)),
            "total_daily_cost": sum(wh.daily_cost for wh in work_hours),
            "total_monthly_cost": sum(wh.monthly_cost for wh in work_hours),
        }

        return render_template(
            "PrintHubWorkHours.html",
            user=current_user,
            config=config,
            active_page="work_hours",
            work_hours=work_hours,
            stats=stats,
            roles=PrintHubWorkHours.get_roles(),
            search_term=search_term,
            filter_role=filter_role,
        )

    except Exception as e:
        flash("Fehler beim Laden der Arbeitszeiten.", "error")
        current_app_logger.error(f"Error loading work hours: {e}")
        return render_template(
            "PrintHubWorkHours.html",
            user=current_user,
            config=config,
            active_page="work_hours",
            work_hours=[],
            stats={
                "total_workers": 0,
                "avg_cost_per_hour": 0,
                "cheapest_worker": None,
                "most_expensive_worker": None,
                "roles": [],
                "total_daily_cost": 0,
                "total_monthly_cost": 0,
            },
            roles=PrintHubWorkHours.get_roles(),
            search_term="",
            filter_role="",
        )


@blueprint.route("/work_hour/delete_work_hour/<int:work_hour_id>", methods=["POST"])
@enabled_required
def delete_work_hour(work_hour_id):
    """Arbeitszeit löschen - nur eigene Arbeitszeiten"""
    try:
        # Arbeitszeit laden und prüfen ob sie dem aktuellen Benutzer gehört
        work_hour = PrintHubWorkHours.query.filter_by(
            id=work_hour_id, created_by=current_user.username
        ).first()

        if not work_hour:
            flash(
                "Arbeitszeit nicht gefunden oder Sie haben keine Berechtigung zum Löschen.",
                "error",
            )
            return redirect(url_for("PrintHub.printHub_work_hours"))

        worker_name = work_hour.name
        worker_role = work_hour.role

        # Arbeitszeit löschen
        db.session.delete(work_hour)
        db.session.commit()

        flash(
            f'Arbeitszeit für "{worker_name}" ({worker_role}) erfolgreich gelöscht!',
            "success",
        )
        current_app_logger.info(
            f"User {current_user.username} deleted work hour: {worker_name} ({worker_role})"
        )

    except Exception as e:
        flash("Fehler beim Löschen der Arbeitszeit.", "error")
        current_app_logger.error(f"Error deleting work hour: {e}")

    return redirect(url_for("PrintHub.printHub_work_hours"))


@blueprint.route("/api/work_hours", methods=["GET"])
@enabled_required
def api_work_hours():
    """API: Alle Arbeitszeiten als JSON"""
    try:
        work_hours = PrintHubWorkHours.get_by_user(current_user.username)
        return jsonify({"success": True, "data": [wh.to_dict() for wh in work_hours]})
    except Exception as e:
        current_app_logger.error(f"Error in API work hours: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# Zu Ihrer routes.py hinzufügen:


@blueprint.route("/printHub_overhead_profiles", methods=["GET", "POST"])
@enabled_required
def printHub_overhead_profiles():
    """Overhead-Profile-Verwaltung - Anzeigen und Hinzufügen"""

    if request.method == "POST":
        try:
            # Form-Daten extrahieren
            name = request.form.get("profile_name", "").strip()
            location = request.form.get("location", "").strip()
            rent_monthly = request.form.get("rent_monthly", type=float) or 0
            heating_electricity = (
                request.form.get("heating_electricity", type=float) or 0
            )
            insurance = request.form.get("insurance", type=float) or 0
            internet = request.form.get("internet", type=float) or 0
            software_cost = request.form.get("software_cost", type=float) or 0
            software_billing = request.form.get("software_billing", "").strip()
            other_costs = request.form.get("other_costs", type=float) or 0
            planned_hours_monthly = request.form.get("planned_hours_monthly", type=int)
            is_active = request.form.get("is_active") == "on"
            notes = request.form.get("overhead_notes", "").strip()

            # Validierung
            if not name:
                flash("Bitte geben Sie einen Profil-Namen ein!", "error")
                return redirect(url_for("PrintHub.printHub_overhead_profiles"))

            if not planned_hours_monthly or planned_hours_monthly <= 0:
                flash("Geplante Stunden pro Monat müssen größer als 0 sein!", "error")
                return redirect(url_for("PrintHub.printHub_overhead_profiles"))

            if software_billing not in ["monthly", "yearly"]:
                software_billing = "monthly"

            # Neue Overhead-Profil erstellen
            new_overhead_profile = PrintHubOverheadProfile(
                name=name,
                location=location if location else None,
                rent_monthly=rent_monthly,
                heating_electricity=heating_electricity,
                insurance=insurance,
                internet=internet,
                software_cost=software_cost,
                software_billing=software_billing,
                other_costs=other_costs,
                planned_hours_monthly=planned_hours_monthly,
                is_active=is_active,
                notes=notes if notes else None,
                created_by=current_user.username,
                created_at=get_current_time(),
                updated_at=get_current_time(),
            )

            # In Datenbank speichern
            db.session.add(new_overhead_profile)
            db.session.commit()

            flash(f'Overhead-Profil "{name}" erfolgreich hinzugefügt!', "success")
            current_app_logger.info(
                f"User {current_user.username} added overhead profile: {name}"
            )

        except Exception as e:
            flash("Ein unerwarteter Fehler ist aufgetreten.", "error")
            current_app_logger.error(f"Unexpected error adding overhead profile: {e}")

        return redirect(url_for("PrintHub.printHub_overhead_profiles"))

    # GET Request - Overhead-Profile laden
    try:
        # Suchparameter
        search_term = request.args.get("search", "").strip()
        show_inactive = request.args.get("show_inactive", "").strip() == "true"

        # Overhead-Profile laden
        if search_term:
            overhead_profiles = PrintHubOverheadProfile.search(
                username=current_user.username,
                search_term=search_term,
                include_inactive=show_inactive,
            )
        else:
            overhead_profiles = PrintHubOverheadProfile.get_by_user(
                current_user.username, include_inactive=show_inactive
            )

        # Statistiken berechnen
        active_profiles = [op for op in overhead_profiles if op.is_active]

        stats = {
            "total_profiles": len(overhead_profiles),
            "active_profiles": len(active_profiles),
            "avg_overhead_per_hour": (
                sum(op.overhead_per_hour for op in active_profiles)
                / len(active_profiles)
                if active_profiles
                else 0
            ),
            "cheapest_overhead": min(
                active_profiles, key=lambda x: x.overhead_per_hour, default=None
            ),
            "most_expensive_overhead": max(
                active_profiles, key=lambda x: x.overhead_per_hour, default=None
            ),
            "total_monthly_costs": sum(
                op.total_monthly_costs for op in active_profiles
            ),
            "total_planned_hours": sum(
                op.planned_hours_monthly for op in active_profiles
            ),
        }

        return render_template(
            "PrintHubOverheadProfiles.html",
            user=current_user,
            config=config,
            active_page="overhead_profiles",
            overhead_profiles=overhead_profiles,
            stats=stats,
            software_billing_options=PrintHubOverheadProfile.get_software_billing_options(),
            search_term=search_term,
            show_inactive=show_inactive,
        )

    except Exception as e:
        flash("Fehler beim Laden der Overhead-Profile.", "error")
        current_app_logger.error(f"Error loading overhead profiles: {e}")
        return render_template(
            "PrintHubOverheadProfiles.html",
            user=current_user,
            config=config,
            active_page="overhead_profiles",
            overhead_profiles=[],
            stats={
                "total_profiles": 0,
                "active_profiles": 0,
                "avg_overhead_per_hour": 0,
                "cheapest_overhead": None,
                "most_expensive_overhead": None,
                "total_monthly_costs": 0,
                "total_planned_hours": 0,
            },
            software_billing_options=PrintHubOverheadProfile.get_software_billing_options(),
            search_term="",
            show_inactive=False,
        )


@blueprint.route(
    "/overhead_profile/delete_overhead_profile/<int:profile_id>", methods=["POST"]
)
@enabled_required
def delete_overhead_profile(profile_id):
    """Overhead-Profil löschen - nur eigene Profile"""
    try:
        # Overhead-Profil laden und prüfen ob es dem aktuellen Benutzer gehört
        overhead_profile = PrintHubOverheadProfile.query.filter_by(
            id=profile_id, created_by=current_user.username
        ).first()

        if not overhead_profile:
            flash(
                "Overhead-Profil nicht gefunden oder Sie haben keine Berechtigung zum Löschen.",
                "error",
            )
            return redirect(url_for("PrintHub.printHub_overhead_profiles"))

        profile_name = overhead_profile.name
        profile_location = overhead_profile.location

        # Overhead-Profil löschen
        db.session.delete(overhead_profile)
        db.session.commit()

        location_text = f" ({profile_location})" if profile_location else ""
        flash(
            f'Overhead-Profil "{profile_name}"{location_text} erfolgreich gelöscht!',
            "success",
        )
        current_app_logger.info(
            f"User {current_user.username} deleted overhead profile: {profile_name}"
        )

    except Exception as e:
        flash("Fehler beim Löschen des Overhead-Profils.", "error")
        current_app_logger.error(f"Error deleting overhead profile: {e}")

    return redirect(url_for("PrintHub.printHub_overhead_profiles"))


@blueprint.route("/api/overhead_profiles", methods=["GET"])
@enabled_required
def api_overhead_profiles():
    """API: Alle Overhead-Profile als JSON"""
    try:
        show_inactive = request.args.get("show_inactive", "false").lower() == "true"
        overhead_profiles = PrintHubOverheadProfile.get_by_user(
            current_user.username, include_inactive=show_inactive
        )

        return jsonify(
            {"success": True, "data": [op.to_dict() for op in overhead_profiles]}
        )
    except Exception as e:
        current_app_logger.error(f"Error in API overhead profiles: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route("/printHub_discount_profiles", methods=["GET", "POST"])
@enabled_required
def printHub_discount_profiles():
    """Rabatte-Profile-Verwaltung - Anzeigen und Hinzufügen"""

    # Discount Types für das Template aus dem Model laden
    try:
        discount_types = PrintHubDiscountProfile.get_discount_types()

    except Exception as e:
        discount_types = [("discount", "Rabatt"), ("surcharge", "Aufschlag")]

    if request.method == "POST":

        try:
            name = request.form.get("discount_name", "").strip()
            discount_type = request.form.get("discount_type", "").strip()
            percentage = request.form.get("percentage", type=float)
            notes = request.form.get("discount_notes", "").strip()
            is_active = request.form.get("is_active") == "on"

            if not name:

                flash("Bitte geben Sie einen Namen für das Profil ein!", "error")
                return redirect(url_for("PrintHub.printHub_discount_profiles"))

            if discount_type not in ["discount", "surcharge"]:

                flash(
                    "Bitte wählen Sie einen gültigen Typ (Rabatt oder Aufschlag)!",
                    "error",
                )
                return redirect(url_for("PrintHub.printHub_discount_profiles"))

            if percentage is None:

                flash("Bitte geben Sie einen Prozentsatz ein!", "error")
                return redirect(url_for("PrintHub.printHub_discount_profiles"))

            if percentage < 0 or percentage > 100:

                flash("Prozentsatz muss zwischen 0% und 100% liegen!", "error")
                return redirect(url_for("PrintHub.printHub_discount_profiles"))

            new_discount_profile = PrintHubDiscountProfile(
                name=name,
                discount_type=discount_type,
                percentage=percentage,
                notes=notes if notes else None,
                is_active=is_active,
                created_by=current_user.username,
                created_at=get_current_time(),
                updated_at=get_current_time(),
            )

            db.session.add(new_discount_profile)

            db.session.commit()

            type_display = "Rabatt" if discount_type == "discount" else "Aufschlag"
            flash(
                f'{type_display}-Profil "{name}" ({percentage}%) erfolgreich hinzugefügt!',
                "success",
            )

            current_app_logger.info(
                f"User {current_user.username} added {discount_type} profile: {name}"
            )

        except Exception as e:

            traceback.print_exc()

            # Rollback bei Fehler
            db.session.rollback()
            flash("Ein unerwarteter Fehler ist aufgetreten.", "error")
            current_app_logger.error(f"Unexpected error adding discount profile: {e}")

        return redirect(url_for("PrintHub.printHub_discount_profiles"))

    try:
        # Suchparameter
        search_term = request.args.get("search", "").strip()
        show_inactive = request.args.get("show_inactive", "").strip() == "true"

        all_profiles = PrintHubDiscountProfile.query.all()

        # Jetzt mit Benutzer-Filter

        user_profiles = PrintHubDiscountProfile.query.filter_by(
            created_by=current_user.username
        ).all()

        # Rabatte-Profile laden
        if search_term:

            discount_profiles = PrintHubDiscountProfile.search(
                username=current_user.username,
                search_term=search_term,
                include_inactive=show_inactive,
            )
        else:

            discount_profiles = PrintHubDiscountProfile.get_by_user(
                current_user.username, include_inactive=show_inactive
            )

        # Statistiken berechnen
        active_profiles = [dp for dp in discount_profiles if dp.is_active]

        stats = {
            "total_profiles": len(discount_profiles),
            "active_profiles": len(active_profiles),
            "discount_profiles": len([dp for dp in active_profiles if dp.is_discount]),
            "surcharge_profiles": len(
                [dp for dp in active_profiles if dp.is_surcharge]
            ),
            "avg_percentage": (
                sum(float(dp.percentage) for dp in active_profiles)
                / len(active_profiles)
                if active_profiles
                else 0
            ),
            "highest_percentage": max(
                active_profiles, key=lambda x: x.percentage, default=None
            ),
            "lowest_percentage": min(
                active_profiles, key=lambda x: x.percentage, default=None
            ),
        }

        return render_template(
            "PrintHubDiscountProfiles.html",
            user=current_user,
            config=config,
            active_page="discount_profiles",
            discount_profiles=discount_profiles,
            discount_types=discount_types,
            stats=stats,
            search_term=search_term,
            show_inactive=show_inactive,
        )

    except Exception as e:
        flash("Fehler beim Laden der Rabatt-Profile.", "error")
        current_app_logger.error(f"Error loading discount profiles: {e}")

        # Statistik-Struktur für Fehlerfall
        empty_stats = {
            "total_profiles": 0,
            "active_profiles": 0,
            "discount_profiles": 0,
            "surcharge_profiles": 0,
            "avg_percentage": 0,
            "highest_percentage": None,
            "lowest_percentage": None,
        }

        return render_template(
            "PrintHubDiscountProfiles.html",
            user=current_user,
            config=config,
            active_page="discount_profiles",
            discount_profiles=[],
            discount_types=discount_types,
            stats=empty_stats,
            search_term="",
            show_inactive=False,
        )


@blueprint.route(
    "/discount_profile/delete_discount_profile/<int:profile_id>", methods=["POST"]
)
@enabled_required
def delete_discount_profile(profile_id):
    """Rabatt-Profil löschen - nur eigene Profile"""
    try:
        # Rabatt-Profil laden und prüfen ob es dem aktuellen Benutzer gehört
        discount_profile = PrintHubDiscountProfile.query.filter_by(
            id=profile_id, created_by=current_user.username
        ).first()

        if not discount_profile:
            flash(
                "Rabatt-Profil nicht gefunden oder Sie haben keine Berechtigung zum Löschen.",
                "error",
            )
            return redirect(url_for("PrintHub.printHub_discount_profiles"))

        profile_name = discount_profile.name
        discount_percentage = discount_profile.percentage
        discount_type_display = discount_profile.discount_type_display

        # Rabatt-Profil löschen
        db.session.delete(discount_profile)
        db.session.commit()

        flash(
            f'{discount_type_display}-Profil "{profile_name}" ({discount_percentage}%) erfolgreich gelöscht!',
            "success",
        )
        current_app_logger.info(
            f"User {current_user.username} deleted {discount_profile.discount_type} profile: {profile_name}"
        )

    except Exception as e:
        flash("Fehler beim Löschen des Rabatt-Profils.", "error")
        current_app_logger.error(f"Error deleting discount profile: {e}")

    return redirect(url_for("PrintHub.printHub_discount_profiles"))


@blueprint.route("/api/discount_profiles", methods=["GET"])
@enabled_required
def api_discount_profiles():
    """API: Alle Rabatt-Profile als JSON"""
    try:
        show_inactive = request.args.get("show_inactive", "false").lower() == "true"
        search_term = request.args.get("search", "").strip()

        # Profile laden
        if search_term:
            discount_profiles = PrintHubDiscountProfile.search(
                username=current_user.username,
                search_term=search_term,
                include_inactive=show_inactive,
            )
        else:
            discount_profiles = PrintHubDiscountProfile.get_by_user(
                current_user.username, include_inactive=show_inactive
            )

        # Statistiken berechnen
        active_profiles = [dp for dp in discount_profiles if dp.is_active]
        stats = {
            "total_profiles": len(discount_profiles),
            "active_profiles": len(active_profiles),
            "discount_profiles": len([dp for dp in active_profiles if dp.is_discount]),
            "surcharge_profiles": len(
                [dp for dp in active_profiles if dp.is_surcharge]
            ),
            "avg_percentage": (
                sum(float(dp.percentage) for dp in active_profiles)
                / len(active_profiles)
                if active_profiles
                else 0
            ),
        }

        return jsonify(
            {
                "success": True,
                "data": [dp.to_dict() for dp in discount_profiles],
                "stats": stats,
            }
        )

    except Exception as e:
        current_app_logger.error(f"Error in API discount profiles: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route("/api/discount_profiles/<int:profile_id>/calculate", methods=["POST"])
@enabled_required
def api_calculate_discount(profile_id):
    """API: Berechnet Rabatt/Aufschlag für einen gegebenen Preis"""
    try:
        # Profil laden
        discount_profile = PrintHubDiscountProfile.query.filter_by(
            id=profile_id, created_by=current_user.username
        ).first()

        if not discount_profile:
            return jsonify({"success": False, "error": "Profil nicht gefunden"}), 404

        # Preis aus Request extrahieren
        data = request.get_json()
        if not data or "price" not in data:
            return jsonify({"success": False, "error": "Preis erforderlich"}), 400

        try:
            original_price = float(data["price"])
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Ungültiger Preis"}), 400

        if original_price < 0:
            return jsonify({"success": False, "error": "Preis muss positiv sein"}), 400

        # Berechnung durchführen
        pricing_details = discount_profile.get_pricing_details(original_price)

        return jsonify(
            {
                "success": True,
                "profile": discount_profile.to_dict(),
                "calculation": pricing_details,
            }
        )

    except Exception as e:
        current_app_logger.error(f"Error calculating discount: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route("/printHub_quote_calculator", methods=["GET", "POST"])
@blueprint.route(
    "/printHub_quote_calculator/<int:quote_id>/edit", methods=["GET", "POST"]
)
@enabled_required
def printHub_quote_calculator(quote_id=None):
    """3D-Druck Offerten-Rechner - Neu erstellen oder bearbeiten"""

    if quote_id is None and request.method == "GET":
        quote_id = request.args.get("quote_id", type=int)

    # Edit-Modus: Bestehende Quote laden
    edit_quote = None
    if quote_id:
        edit_quote = PrintHubQuote.query.filter_by(
            id=quote_id, created_by=current_user.username
        ).first_or_404()

        # Nur Entwürfe können bearbeitet werden
        if edit_quote.status != "draft":
            flash("Nur Entwürfe können bearbeitet werden.", "error")
            return redirect(
                url_for("PrintHub.printHub_quote_detail", quote_id=quote_id)
            )

    if request.method == "POST":
        try:
            # Hauptauftrag-Daten
            order_name = request.form.get("order_name", "").strip()
            customer_name = request.form.get("customer_name", "").strip()

            # Globale Kalkulationsgrundlagen
            global_printer_id = request.form.get("global_3d_printer", type=int)
            global_energy_profile_id = request.form.get(
                "global_energy_profile", type=int
            )
            global_work_profile_id = request.form.get("global_work_profile", type=int)
            global_overhead_profile_id = request.form.get(
                "global_overhead_profile", type=int
            )
            global_discount_profile_id = request.form.get(
                "global_discount_profile", type=int
            )

            # Validierung
            if not order_name:
                flash("Bitte geben Sie einen Auftragsnamen ein!", "error")
                return redirect(request.url)

            # Subaufträge verarbeiten
            suborders = []
            suborder_count = int(request.form.get("suborder_count", 0))

            for i in range(suborder_count):
                suborder_name = request.form.get(f"suborder_name_{i}", "").strip()
                filament_id = request.form.get(f"filament_id_{i}", type=int)
                print_time_hours = request.form.get(f"print_time_hours_{i}", type=float)
                work_time_hours = request.form.get(f"work_time_hours_{i}", type=float)
                filament_usage_grams = request.form.get(
                    f"filament_usage_grams_{i}", type=int
                )

                # Individuelle Profile (optional)
                use_individual = request.form.get(f"use_individual_calc_{i}") == "on"
                individual_printer_id = (
                    request.form.get(f"individual_printer_{i}", type=int)
                    if use_individual
                    else None
                )
                individual_energy_id = (
                    request.form.get(f"individual_energy_profile_{i}", type=int)
                    if use_individual
                    else None
                )
                individual_work_id = (
                    request.form.get(f"individual_work_profile_{i}", type=int)
                    if use_individual
                    else None
                )
                individual_overhead_id = (
                    request.form.get(f"individual_overhead_profile_{i}", type=int)
                    if use_individual
                    else None
                )

                if (
                    suborder_name
                    and filament_id
                    and print_time_hours is not None
                    and work_time_hours is not None
                    and filament_usage_grams
                ):

                    suborders.append(
                        {
                            "name": suborder_name,
                            "filament_id": filament_id,
                            "print_time_hours": print_time_hours,
                            "work_time_hours": work_time_hours,
                            "filament_usage_grams": filament_usage_grams,
                            "use_individual": use_individual,
                            "individual_printer_id": individual_printer_id,
                            "individual_energy_id": individual_energy_id,
                            "individual_work_id": individual_work_id,
                            "individual_overhead_id": individual_overhead_id,
                        }
                    )

            if not suborders:
                flash("Bitte fügen Sie mindestens einen Druckauftrag hinzu!", "error")
                return redirect(request.url)

            # Quote berechnen und speichern/aktualisieren
            if edit_quote:
                # Bestehende Quote aktualisieren
                quote = update_existing_quote(
                    quote=edit_quote,
                    order_name=order_name,
                    customer_name=customer_name,
                    global_printer_id=global_printer_id,
                    global_energy_profile_id=global_energy_profile_id,
                    global_work_profile_id=global_work_profile_id,
                    global_overhead_profile_id=global_overhead_profile_id,
                    global_discount_profile_id=global_discount_profile_id,
                    suborders=suborders,
                )
                flash("Offerte erfolgreich aktualisiert!", "success")
            else:
                # Neue Quote erstellen
                quote = calculate_and_save_quote(
                    username=current_user.username,
                    order_name=order_name,
                    customer_name=customer_name,
                    global_printer_id=global_printer_id,
                    global_energy_profile_id=global_energy_profile_id,
                    global_work_profile_id=global_work_profile_id,
                    global_overhead_profile_id=global_overhead_profile_id,
                    global_discount_profile_id=global_discount_profile_id,
                    suborders=suborders,
                )
                flash("Offerte erfolgreich erstellt!", "success")

            if quote:
                return redirect(
                    url_for("PrintHub.printHub_quote_detail", quote_id=quote.id)
                )
            else:
                flash("Fehler beim Speichern der Offerte.", "error")

        except Exception as e:
            flash(f"Fehler bei der Berechnung: {str(e)}", "error")
            current_app_logger.error(f"Quote calculation error: {e}")

        return redirect(request.url)

    # GET Request - Formular anzeigen
    try:
        # Alle verfügbaren Profile laden
        printers = PrintHubPrinter.get_by_user(current_user.username)
        filaments = PrintHubFilament.get_by_user(current_user.username)
        energy_profiles = PrintHubEnergyCost.get_by_user(current_user.username)
        work_profiles = PrintHubWorkHours.get_by_user(current_user.username)
        overhead_profiles = PrintHubOverheadProfile.get_by_user(current_user.username)
        discount_profiles = PrintHubDiscountProfile.get_by_user(current_user.username)

        # Edit-Mode: Daten für Vorausfüllung vorbereiten
        edit_data = None
        if edit_quote:
            edit_data = prepare_edit_data(edit_quote)

        return render_template(
            "PrintHubQuoteCalculator.html",
            user=current_user,
            config=config,
            active_page="quote_calculator",
            printers=printers,
            filaments=filaments,
            energy_profiles=energy_profiles,
            work_profiles=work_profiles,
            overhead_profiles=overhead_profiles,
            discount_profiles=discount_profiles,
            current_date=datetime.now().strftime("%d.%m.%Y"),
            edit_quote=edit_quote,
            edit_data=edit_data,
            is_edit_mode=bool(edit_quote),
        )

    except Exception as e:
        flash(f"Fehler beim Laden der Kalkulationsseite: {e}", "error")
        current_app_logger.error(f"Error loading quote calculator: {e}")
        return redirect(url_for("PrintHub.PrintHub_index"))


def calculate_quote(username, order_name, customer_name, suborders):
    """Berechnet die Offerte für einen Auftrag"""

    total_cost = 0
    total_time = 0
    suborder_details = []

    for suborder in suborders:
        # Drucker laden
        printer = PrintHubPrinter.query.filter_by(
            id=suborder["printer_id"], created_by=username
        ).first()

        # Filament laden
        filament = PrintHubFilament.query.filter_by(
            id=suborder["filament_id"], created_by=username
        ).first()

        if not printer or not filament:
            continue

        # Kosten berechnen
        print_time_hours = suborder["print_time_hours"]
        filament_usage_grams = suborder["filament_usage_grams"]

        # Maschinenkosten
        machine_cost = float(printer.machine_cost_per_hour) * print_time_hours

        # Filamentkosten
        filament_cost_per_gram = float(filament.price) / filament.weight
        filament_cost = filament_cost_per_gram * filament_usage_grams

        # Energiekosten (falls verfügbar)
        energy_cost = 0
        if printer.energy_consumption:
            energy_kwh = (printer.energy_consumption / 1000) * print_time_hours
            energy_cost = energy_kwh * 0.25  # 0.25 CHF pro kWh

        # Subauftrag-Gesamtkosten
        suborder_total = machine_cost + filament_cost + energy_cost

        suborder_details.append(
            {
                "name": suborder["name"],
                "printer_name": printer.name,
                "filament_name": f"{filament.manufacturer} {filament.name}",
                "print_time_hours": print_time_hours,
                "filament_usage_grams": filament_usage_grams,
                "machine_cost": round(machine_cost, 2),
                "filament_cost": round(filament_cost, 2),
                "energy_cost": round(energy_cost, 2),
                "suborder_total": round(suborder_total, 2),
            }
        )

        total_cost += suborder_total
        total_time += print_time_hours

    # Ergebnis zusammenstellen
    quote_result = {
        "order_name": order_name,
        "customer_name": customer_name,
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "suborders": suborder_details,
        "total_cost": round(total_cost, 2),
        "total_time": round(total_time, 2),
        "cost_breakdown": {
            "machine_cost": round(sum(s["machine_cost"] for s in suborder_details), 2),
            "filament_cost": round(
                sum(s["filament_cost"] for s in suborder_details), 2
            ),
            "energy_cost": round(sum(s["energy_cost"] for s in suborder_details), 2),
        },
    }

    return quote_result


def calculate_and_save_quote(
    username,
    order_name,
    customer_name,
    global_printer_id,
    global_energy_profile_id,
    global_work_profile_id,
    global_overhead_profile_id,
    global_discount_profile_id,
    suborders,
):
    """Berechnet eine Offerte und speichert sie in der Datenbank"""

    try:
        # Globale Profile laden
        global_printer = (
            PrintHubPrinter.query.get(global_printer_id) if global_printer_id else None
        )
        global_energy = (
            PrintHubEnergyCost.query.get(global_energy_profile_id)
            if global_energy_profile_id
            else None
        )
        global_work = (
            PrintHubWorkHours.query.get(global_work_profile_id)
            if global_work_profile_id
            else None
        )
        global_overhead = (
            PrintHubOverheadProfile.query.get(global_overhead_profile_id)
            if global_overhead_profile_id
            else None
        )
        global_discount = (
            PrintHubDiscountProfile.query.get(global_discount_profile_id)
            if global_discount_profile_id
            else None
        )

        # Quote-Objekt erstellen
        quote = PrintHubQuote(
            order_name=order_name,
            customer_name=customer_name,
            global_printer_id=global_printer_id,
            global_energy_profile_id=global_energy_profile_id,
            global_work_profile_id=global_work_profile_id,
            global_overhead_profile_id=global_overhead_profile_id,
            global_discount_profile_id=global_discount_profile_id,
            total_cost=0,
            total_time=0,
            total_work_time=0,
            created_by=username,
        )

        total_cost = 0
        total_time = 0
        total_work_time = 0
        total_machine_cost = 0
        total_material_cost = 0
        total_energy_cost = 0
        total_work_cost = 0
        total_overhead_cost = 0

        suborder_objects = []

        for suborder_data in suborders:
            # Filament laden
            filament = PrintHubFilament.query.get(suborder_data["filament_id"])
            if not filament:
                continue

            # Profile bestimmen (individuell oder global)
            if suborder_data["use_individual"]:
                printer = (
                    PrintHubPrinter.query.get(suborder_data["individual_printer_id"])
                    if suborder_data["individual_printer_id"]
                    else global_printer
                )
                energy = (
                    PrintHubEnergyCost.query.get(suborder_data["individual_energy_id"])
                    if suborder_data["individual_energy_id"]
                    else global_energy
                )
                work = (
                    PrintHubWorkHours.query.get(suborder_data["individual_work_id"])
                    if suborder_data["individual_work_id"]
                    else global_work
                )
                overhead = (
                    PrintHubOverheadProfile.query.get(
                        suborder_data["individual_overhead_id"]
                    )
                    if suborder_data["individual_overhead_id"]
                    else global_overhead
                )
            else:
                printer = global_printer
                energy = global_energy
                work = global_work
                overhead = global_overhead

            # Kosten berechnen
            print_time = suborder_data["print_time_hours"]
            work_time = suborder_data["work_time_hours"]
            usage_grams = suborder_data["filament_usage_grams"]

            # Maschinenkosten
            machine_cost = (
                float(printer.machine_cost_per_hour if printer else 0) * print_time
            )

            # Materialkosten
            material_cost = (float(filament.price) / filament.weight) * usage_grams

            # Energiekosten
            energy_cost = print_time * float(energy.cost_per_kwh if energy else 0.25)

            # Arbeitskosten (verwende individuelle Arbeitszeit!)
            work_cost = work_time * float(work.cost_per_hour if work else 0)

            # Overhead-Kosten
            overhead_cost = print_time * float(
                overhead.overhead_per_hour if overhead else 0
            )

            # Suborder-Total vor Rabatt/Aufschlag
            suborder_subtotal = (
                machine_cost + material_cost + energy_cost + work_cost + overhead_cost
            )

            # SubOrder-Objekt erstellen
            suborder_obj = PrintHubSubOrder(
                name=suborder_data["name"],
                filament_id=suborder_data["filament_id"],
                filament_usage_grams=usage_grams,
                print_time_hours=print_time,
                work_time_hours=work_time,
                printer_id=printer.id if printer else None,
                energy_profile_id=energy.id if energy else None,
                work_profile_id=work.id if work else None,
                overhead_profile_id=overhead.id if overhead else None,
                machine_cost=machine_cost,
                material_cost=material_cost,
                energy_cost=energy_cost,
                work_cost=work_cost,
                overhead_cost=overhead_cost,
                suborder_total=suborder_subtotal,
                # Snapshot-Daten für Historisierung
                printer_name=printer.name if printer else "Nicht definiert",
                filament_name=f"{filament.manufacturer} {filament.name}",
                printer_cost_per_hour=printer.machine_cost_per_hour if printer else 0,
                energy_cost_per_kwh=energy.cost_per_kwh if energy else 0.25,
                work_cost_per_hour=work.cost_per_hour if work else 0,
                overhead_cost_per_hour=overhead.overhead_per_hour if overhead else 0,
            )

            suborder_objects.append(suborder_obj)

            # Totals aktualisieren
            total_cost += suborder_subtotal
            total_time += print_time
            total_work_time += work_time
            total_machine_cost += machine_cost
            total_material_cost += material_cost
            total_energy_cost += energy_cost
            total_work_cost += work_cost
            total_overhead_cost += overhead_cost

        # Globaler Rabatt/Aufschlag anwenden
        if global_discount:
            total_cost = global_discount.calculate_final_price(total_cost)

        # Quote-Totals setzen
        quote.total_cost = total_cost
        quote.total_time = total_time
        quote.total_work_time = total_work_time
        quote.total_machine_cost = total_machine_cost
        quote.total_material_cost = total_material_cost
        quote.total_energy_cost = total_energy_cost
        quote.total_work_cost = total_work_cost
        quote.total_overhead_cost = total_overhead_cost

        # In Datenbank speichern
        db.session.add(quote)
        db.session.flush()  # Um quote.id zu bekommen

        # SubOrders hinzufügen
        for suborder_obj in suborder_objects:
            suborder_obj.quote_id = quote.id
            db.session.add(suborder_obj)

        db.session.commit()

        return quote

    except Exception as e:
        db.session.rollback()
        current_app_logger.error(f"Error calculating and saving quote: {e}")
        return None


def create_quote_display_data(quote):
    """Erstellt Anzeige-Daten für das Frontend"""
    return {
        "id": quote.id,
        "order_name": quote.order_name,
        "customer_name": quote.customer_name,
        "created_at": quote.created_at.strftime("%d.%m.%Y %H:%M"),
        "total_cost": float(quote.total_cost),
        "total_time": float(quote.total_time),
        "total_work_time": float(quote.total_work_time),
        "suborders": [suborder.to_dict() for suborder in quote.suborders],
        "cost_breakdown": {
            "machine_cost": float(quote.total_machine_cost),
            "filament_cost": float(quote.total_material_cost),
            "energy_cost": float(quote.total_energy_cost),
            "work_cost": float(quote.total_work_cost),
            "overhead_cost": float(quote.total_overhead_cost),
        },
    }


@blueprint.route("/printHub_quotes", methods=["GET"])
@enabled_required
def printHub_quotes():
    """Übersicht aller Offerten"""
    try:
        include_archived = request.args.get("include_archived", "false") == "true"
        quotes = PrintHubQuote.get_by_user(
            current_user.username, include_archived=include_archived
        )

        # Statistiken
        stats = {
            "total_quotes": len(quotes),
            "total_value": sum(float(q.total_cost) for q in quotes),
            "avg_quote_value": (
                sum(float(q.total_cost) for q in quotes) / len(quotes) if quotes else 0
            ),
            "status_counts": {},
        }

        # Status-Zählungen
        for quote in quotes:
            status = quote.status
            if status not in stats["status_counts"]:
                stats["status_counts"][status] = 0
            stats["status_counts"][status] += 1

        return render_template(
            "PrintHubQuotes.html",
            user=current_user,
            config=config,
            active_page="quotes",
            quotes=quotes,
            stats=stats,
            include_archived=include_archived,
        )

    except Exception as e:
        flash("Fehler beim Laden der Offerten.", "error")
        current_app_logger.error(f"Error loading quotes: {e}")
        return redirect(url_for("PrintHub.PrintHub_index"))


@blueprint.route("/printHub_quote/<int:quote_id>", methods=["GET"])
@enabled_required
def printHub_quote_detail(quote_id):
    """Detail-Ansicht einer Offerte"""
    try:
        quote = PrintHubQuote.query.filter_by(
            id=quote_id, created_by=current_user.username
        ).first_or_404()

        return render_template(
            "PrintHubQuoteDetail.html",
            user=current_user,
            config=config,
            active_page="quotes",
            quote=quote,
        )

    except Exception as e:
        flash("Offerte nicht gefunden.", "error")
        current_app_logger.error(f"Error loading quote detail: {e}")
        return redirect(url_for("PrintHub.printHub_quotes"))


@blueprint.route("/api/quote/<int:quote_id>/status", methods=["POST"])
@enabled_required
def api_update_quote_status(quote_id):
    """API: Status einer Offerte aktualisieren"""
    try:
        quote = PrintHubQuote.query.filter_by(
            id=quote_id, created_by=current_user.username
        ).first()

        if not quote:
            return jsonify({"success": False, "error": "Offerte nicht gefunden"}), 404

        data = request.get_json()
        new_status = data.get("status")

        valid_statuses = ["draft", "sent", "accepted", "rejected"]
        if new_status not in valid_statuses:
            return jsonify({"success": False, "error": "Ungültiger Status"}), 400

        quote.status = new_status
        quote.updated_at = get_current_time()
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Status auf '{quote.status_display}' aktualisiert",
                "new_status": quote.status,
                "new_status_display": quote.status_display,
            }
        )

    except Exception as e:
        db.session.rollback()
        current_app_logger.error(f"Error updating quote status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route("/api/quote/<int:quote_id>/archive", methods=["POST"])
@enabled_required
def api_toggle_quote_archive(quote_id):
    """API: Offerte archivieren/entarchivieren"""
    try:
        quote = PrintHubQuote.query.filter_by(
            id=quote_id, created_by=current_user.username
        ).first()

        if not quote:
            return jsonify({"success": False, "error": "Offerte nicht gefunden"}), 404

        data = request.get_json()
        archived = data.get("archived", False)

        quote.is_archived = archived
        quote.updated_at = get_current_time()
        db.session.commit()

        action = "archiviert" if archived else "aus dem Archiv geholt"
        return jsonify(
            {
                "success": True,
                "message": f"Offerte '{quote.order_name}' wurde {action}",
                "is_archived": quote.is_archived,
            }
        )

    except Exception as e:
        db.session.rollback()
        current_app_logger.error(f"Error toggling quote archive: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route("/api/quote/<int:quote_id>/duplicate", methods=["POST"])
@enabled_required
def api_duplicate_quote(quote_id):
    """API: Offerte duplizieren"""
    try:
        original_quote = PrintHubQuote.query.filter_by(
            id=quote_id, created_by=current_user.username
        ).first()

        if not original_quote:
            return jsonify({"success": False, "error": "Offerte nicht gefunden"}), 404

        # Neue Quote erstellen
        new_quote = PrintHubQuote(
            order_name=f"{original_quote.order_name} (Kopie)",
            customer_name=original_quote.customer_name,
            global_printer_id=original_quote.global_printer_id,
            global_energy_profile_id=original_quote.global_energy_profile_id,
            global_work_profile_id=original_quote.global_work_profile_id,
            global_overhead_profile_id=original_quote.global_overhead_profile_id,
            global_discount_profile_id=original_quote.global_discount_profile_id,
            total_cost=original_quote.total_cost,
            total_time=original_quote.total_time,
            total_work_time=original_quote.total_work_time,
            total_machine_cost=original_quote.total_machine_cost,
            total_material_cost=original_quote.total_material_cost,
            total_energy_cost=original_quote.total_energy_cost,
            total_work_cost=original_quote.total_work_cost,
            total_overhead_cost=original_quote.total_overhead_cost,
            status="draft",  # Neue Quote ist immer ein Entwurf
            created_by=current_user.username,
        )

        db.session.add(new_quote)
        db.session.flush()  # Um new_quote.id zu bekommen

        # SubOrders duplizieren
        for original_suborder in original_quote.suborders:
            new_suborder = PrintHubSubOrder(
                quote_id=new_quote.id,
                name=original_suborder.name,
                filament_id=original_suborder.filament_id,
                filament_usage_grams=original_suborder.filament_usage_grams,
                print_time_hours=original_suborder.print_time_hours,
                work_time_hours=original_suborder.work_time_hours,
                printer_id=original_suborder.printer_id,
                energy_profile_id=original_suborder.energy_profile_id,
                work_profile_id=original_suborder.work_profile_id,
                overhead_profile_id=original_suborder.overhead_profile_id,
                machine_cost=original_suborder.machine_cost,
                material_cost=original_suborder.material_cost,
                energy_cost=original_suborder.energy_cost,
                work_cost=original_suborder.work_cost,
                overhead_cost=original_suborder.overhead_cost,
                suborder_total=original_suborder.suborder_total,
                printer_name=original_suborder.printer_name,
                filament_name=original_suborder.filament_name,
                printer_cost_per_hour=original_suborder.printer_cost_per_hour,
                energy_cost_per_kwh=original_suborder.energy_cost_per_kwh,
                work_cost_per_hour=original_suborder.work_cost_per_hour,
                overhead_cost_per_hour=original_suborder.overhead_cost_per_hour,
            )
            db.session.add(new_suborder)

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Offerte '{original_quote.order_name}' wurde dupliziert",
                "new_quote_id": new_quote.id,
                "new_quote_name": new_quote.order_name,
            }
        )

    except Exception as e:
        db.session.rollback()
        current_app_logger.error(f"Error duplicating quote: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route("/api/quote/<int:quote_id>", methods=["DELETE"])
@enabled_required
def api_delete_quote(quote_id):
    """API: Offerte löschen (nur Entwürfe)"""
    try:
        quote = PrintHubQuote.query.filter_by(
            id=quote_id, created_by=current_user.username
        ).first()

        if not quote:
            return jsonify({"success": False, "error": "Offerte nicht gefunden"}), 404

        if quote.status != "draft":
            return (
                jsonify(
                    {"success": False, "error": "Nur Entwürfe können gelöscht werden"}
                ),
                400,
            )

        quote_name = quote.order_name

        # Quote und alle SubOrders löschen (CASCADE)
        db.session.delete(quote)
        db.session.commit()

        return jsonify(
            {"success": True, "message": f"Offerte '{quote_name}' wurde gelöscht"}
        )

    except Exception as e:
        db.session.rollback()
        current_app_logger.error(f"Error deleting quote: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@blueprint.route("/api/quotes", methods=["GET"])
@enabled_required
def api_quotes():
    """API: Alle Offerten als JSON"""
    try:
        include_archived = (
            request.args.get("include_archived", "false").lower() == "true"
        )
        quotes = PrintHubQuote.get_by_user(
            current_user.username, include_archived=include_archived
        )

        return jsonify(
            {
                "success": True,
                "data": [quote.to_dict() for quote in quotes],
                "total": len(quotes),
            }
        )

    except Exception as e:
        current_app_logger.error(f"Error in API quotes: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def update_existing_quote(
    quote,
    order_name,
    customer_name,
    global_printer_id,
    global_energy_profile_id,
    global_work_profile_id,
    global_overhead_profile_id,
    global_discount_profile_id,
    suborders,
):
    """Aktualisiert eine bestehende Quote"""

    try:
        # Globale Profile laden
        global_printer = (
            PrintHubPrinter.query.get(global_printer_id) if global_printer_id else None
        )
        global_energy = (
            PrintHubEnergyCost.query.get(global_energy_profile_id)
            if global_energy_profile_id
            else None
        )
        global_work = (
            PrintHubWorkHours.query.get(global_work_profile_id)
            if global_work_profile_id
            else None
        )
        global_overhead = (
            PrintHubOverheadProfile.query.get(global_overhead_profile_id)
            if global_overhead_profile_id
            else None
        )
        global_discount = (
            PrintHubDiscountProfile.query.get(global_discount_profile_id)
            if global_discount_profile_id
            else None
        )

        # Quote-Daten aktualisieren
        quote.order_name = order_name
        quote.customer_name = customer_name
        quote.global_printer_id = global_printer_id
        quote.global_energy_profile_id = global_energy_profile_id
        quote.global_work_profile_id = global_work_profile_id
        quote.global_overhead_profile_id = global_overhead_profile_id
        quote.global_discount_profile_id = global_discount_profile_id
        quote.updated_at = get_current_time()

        # Alte SubOrders löschen
        for old_suborder in quote.suborders:
            db.session.delete(old_suborder)

        # Neue Berechnungen
        total_cost = 0
        total_time = 0
        total_work_time = 0
        total_machine_cost = 0
        total_material_cost = 0
        total_energy_cost = 0
        total_work_cost = 0
        total_overhead_cost = 0

        # Neue SubOrders erstellen
        for suborder_data in suborders:
            # Filament laden
            filament = PrintHubFilament.query.get(suborder_data["filament_id"])
            if not filament:
                continue

            # Profile bestimmen (individuell oder global)
            if suborder_data["use_individual"]:
                printer = (
                    PrintHubPrinter.query.get(suborder_data["individual_printer_id"])
                    if suborder_data["individual_printer_id"]
                    else global_printer
                )
                energy = (
                    PrintHubEnergyCost.query.get(suborder_data["individual_energy_id"])
                    if suborder_data["individual_energy_id"]
                    else global_energy
                )
                work = (
                    PrintHubWorkHours.query.get(suborder_data["individual_work_id"])
                    if suborder_data["individual_work_id"]
                    else global_work
                )
                overhead = (
                    PrintHubOverheadProfile.query.get(
                        suborder_data["individual_overhead_id"]
                    )
                    if suborder_data["individual_overhead_id"]
                    else global_overhead
                )
            else:
                printer = global_printer
                energy = global_energy
                work = global_work
                overhead = global_overhead

            # Kosten berechnen
            print_time = suborder_data["print_time_hours"]
            work_time = suborder_data["work_time_hours"]
            usage_grams = suborder_data["filament_usage_grams"]

            # Maschinenkosten
            machine_cost = (
                float(printer.machine_cost_per_hour if printer else 0) * print_time
            )

            # Materialkosten
            material_cost = (float(filament.price) / filament.weight) * usage_grams

            # Energiekosten
            energy_cost = print_time * float(energy.cost_per_kwh if energy else 0.25)

            # Arbeitskosten (verwende individuelle Arbeitszeit!)
            work_cost = work_time * float(work.cost_per_hour if work else 0)

            # Overhead-Kosten
            overhead_cost = print_time * float(
                overhead.overhead_per_hour if overhead else 0
            )

            # Suborder-Total vor Rabatt/Aufschlag
            suborder_subtotal = (
                machine_cost + material_cost + energy_cost + work_cost + overhead_cost
            )

            # SubOrder-Objekt erstellen
            suborder_obj = PrintHubSubOrder(
                quote_id=quote.id,
                name=suborder_data["name"],
                filament_id=suborder_data["filament_id"],
                filament_usage_grams=usage_grams,
                print_time_hours=print_time,
                work_time_hours=work_time,
                printer_id=printer.id if printer else None,
                energy_profile_id=energy.id if energy else None,
                work_profile_id=work.id if work else None,
                overhead_profile_id=overhead.id if overhead else None,
                machine_cost=machine_cost,
                material_cost=material_cost,
                energy_cost=energy_cost,
                work_cost=work_cost,
                overhead_cost=overhead_cost,
                suborder_total=suborder_subtotal,
                # Snapshot-Daten für Historisierung
                printer_name=printer.name if printer else "Nicht definiert",
                filament_name=f"{filament.manufacturer} {filament.name}",
                printer_cost_per_hour=printer.machine_cost_per_hour if printer else 0,
                energy_cost_per_kwh=energy.cost_per_kwh if energy else 0.25,
                work_cost_per_hour=work.cost_per_hour if work else 0,
                overhead_cost_per_hour=overhead.overhead_per_hour if overhead else 0,
            )

            db.session.add(suborder_obj)

            # Totals aktualisieren
            total_cost += suborder_subtotal
            total_time += print_time
            total_work_time += work_time
            total_machine_cost += machine_cost
            total_material_cost += material_cost
            total_energy_cost += energy_cost
            total_work_cost += work_cost
            total_overhead_cost += overhead_cost

        # Globaler Rabatt/Aufschlag anwenden
        if global_discount:
            total_cost = global_discount.calculate_final_price(total_cost)

        # Quote-Totals aktualisieren
        quote.total_cost = total_cost
        quote.total_time = total_time
        quote.total_work_time = total_work_time
        quote.total_machine_cost = total_machine_cost
        quote.total_material_cost = total_material_cost
        quote.total_energy_cost = total_energy_cost
        quote.total_work_cost = total_work_cost
        quote.total_overhead_cost = total_overhead_cost

        # In Datenbank speichern
        db.session.commit()

        # Ergebnis in Session für Anzeige speichern
        session["last_quote_result"] = create_quote_display_data(quote)

        return quote

    except Exception as e:
        db.session.rollback()
        current_app_logger.error(f"Error updating quote: {e}")
        return None


def create_quote_display_data(quote):
    """Erstellt Anzeige-Daten für das Frontend (falls noch nicht vorhanden)"""
    return {
        "id": quote.id,
        "order_name": quote.order_name,
        "customer_name": quote.customer_name,
        "created_at": quote.created_at.strftime("%d.%m.%Y %H:%M"),
        "total_cost": float(quote.total_cost),
        "total_time": float(quote.total_time),
        "total_work_time": float(quote.total_work_time),
        "suborders": [suborder.to_dict() for suborder in quote.suborders],
        "cost_breakdown": {
            "machine_cost": float(quote.total_machine_cost),
            "filament_cost": float(quote.total_material_cost),
            "energy_cost": float(quote.total_energy_cost),
            "work_cost": float(quote.total_work_cost),
            "overhead_cost": float(quote.total_overhead_cost),
        },
    }


def prepare_edit_data(quote):
    """Bereitet Quote-Daten für die Bearbeitung vor"""

    edit_data = {
        "order_name": quote.order_name,
        "customer_name": quote.customer_name,
        "global_printer_id": quote.global_printer_id,
        "global_energy_profile_id": quote.global_energy_profile_id,
        "global_work_profile_id": quote.global_work_profile_id,
        "global_overhead_profile_id": quote.global_overhead_profile_id,
        "global_discount_profile_id": quote.global_discount_profile_id,
        "suborders": [],
    }

    # SubOrders für Vorausfüllung vorbereiten
    for suborder in quote.suborders:
        suborder_data = {
            "name": suborder.name,
            "filament_id": suborder.filament_id,
            "print_time_hours": float(suborder.print_time_hours),
            "work_time_hours": float(suborder.work_time_hours),
            "filament_usage_grams": suborder.filament_usage_grams,
            "printer_id": suborder.printer_id,
            "energy_profile_id": suborder.energy_profile_id,
            "work_profile_id": suborder.work_profile_id,
            "overhead_profile_id": suborder.overhead_profile_id,
            # Bestimme ob individuelle Einstellungen verwendet werden
            "use_individual": (
                suborder.printer_id != quote.global_printer_id
                or suborder.energy_profile_id != quote.global_energy_profile_id
                or suborder.work_profile_id != quote.global_work_profile_id
                or suborder.overhead_profile_id != quote.global_overhead_profile_id
            ),
        }
        edit_data["suborders"].append(suborder_data)

    return edit_data


# Zusätzliche Route für einfache Bearbeitung von der Detail-Seite
@blueprint.route("/api/quote/<int:quote_id>/edit_redirect", methods=["GET"])
@enabled_required
def api_quote_edit_redirect(quote_id):
    """Redirect zur Bearbeitung mit besserer URL"""
    try:
        quote = PrintHubQuote.query.filter_by(
            id=quote_id, created_by=current_user.username
        ).first()

        if not quote:
            return jsonify({"success": False, "error": "Offerte nicht gefunden"}), 404

        if quote.status != "draft":
            return (
                jsonify(
                    {"success": False, "error": "Nur Entwürfe können bearbeitet werden"}
                ),
                400,
            )

        return jsonify(
            {
                "success": True,
                "redirect_url": url_for(
                    "PrintHub.printHub_quote_calculator", quote_id=quote_id
                ),
            }
        )

    except Exception as e:
        current_app_logger.error(f"Error in edit redirect: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# import export


@blueprint.route("/printHub_export_import", methods=["GET", "POST"])
@enabled_required
def printHub_export_import():
    """Export/Import-Verwaltung für PrintHub-Daten"""

    if request.method == "POST":
        action = request.form.get("action")

        if action == "export":
            return handle_export_request()
        elif action == "import":
            return handle_import_request()

    # GET Request - Seite anzeigen
    try:
        # Statistiken für die Übersicht
        stats = get_export_stats(current_user.username)

        return render_template(
            "PrintHubExportImport.html",
            user=current_user,
            config=config,
            active_page="export",
            stats=stats,
        )

    except Exception as e:
        flash("Fehler beim Laden der Export/Import-Seite.", "error")
        current_app_logger.error(f"Error loading export/import page: {e}")
        return redirect(url_for("PrintHub.PrintHub_index"))


def get_export_stats(username):
    """Sammelt Statistiken für die Export-Übersicht"""
    try:
        stats = {
            "filaments": len(PrintHubFilament.get_by_user(username)),
            "printers": len(PrintHubPrinter.get_by_user(username)),
            "energy_costs": len(
                PrintHubEnergyCost.get_by_user(username, include_inactive=True)
            ),
            "work_hours": len(PrintHubWorkHours.get_by_user(username)),
            "overhead_profiles": len(
                PrintHubOverheadProfile.get_by_user(username, include_inactive=True)
            ),
            "discount_profiles": len(
                PrintHubDiscountProfile.get_by_user(username, include_inactive=True)
            ),
            "quotes": len(PrintHubQuote.get_by_user(username, include_archived=True)),
            "suborders": 0,
        }

        # SubOrders zählen
        all_quotes = PrintHubQuote.get_by_user(username, include_archived=True)
        stats["suborders"] = sum(len(quote.suborders) for quote in all_quotes)

        stats["total_records"] = sum(stats.values())

        return stats

    except Exception as e:
        current_app_logger.error(f"Error getting export stats: {e}")
        return {
            "filaments": 0,
            "printers": 0,
            "energy_costs": 0,
            "work_hours": 0,
            "overhead_profiles": 0,
            "discount_profiles": 0,
            "quotes": 0,
            "suborders": 0,
            "total_records": 0,
        }


def handle_export_request():
    """Verarbeitet Export-Anfragen"""
    try:
        export_type = request.form.get("export_type", "all")
        export_format = request.form.get("export_format", "zip")
        include_archived = request.form.get("include_archived") == "on"
        include_inactive = request.form.get("include_inactive") == "on"

        if export_type == "all":
            return export_all_data(export_format, include_archived, include_inactive)
        else:
            return export_single_table(export_type, include_archived, include_inactive)

    except Exception as e:
        flash(f"Fehler beim Export: {str(e)}", "error")
        current_app_logger.error(f"Export error: {e}")
        return redirect(url_for("PrintHub.printHub_export_import"))


def export_all_data(export_format, include_archived=True, include_inactive=True):
    """Exportiert alle Daten als ZIP-Datei"""
    try:
        # ZIP-Datei in Memory erstellen
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Alle Tabellen exportieren
            tables = [
                ("filaments", lambda: export_filaments_csv(current_user.username)),
                ("printers", lambda: export_printers_csv(current_user.username)),
                (
                    "energy_costs",
                    lambda: export_energy_costs_csv(
                        current_user.username, include_inactive
                    ),
                ),
                ("work_hours", lambda: export_work_hours_csv(current_user.username)),
                (
                    "overhead_profiles",
                    lambda: export_overhead_profiles_csv(
                        current_user.username, include_inactive
                    ),
                ),
                (
                    "discount_profiles",
                    lambda: export_discount_profiles_csv(
                        current_user.username, include_inactive
                    ),
                ),
                (
                    "quotes",
                    lambda: export_quotes_csv(current_user.username, include_archived),
                ),
                (
                    "suborders",
                    lambda: export_suborders_csv(
                        current_user.username, include_archived
                    ),
                ),
            ]

            for table_name, export_func in tables:
                try:
                    csv_content = export_func()
                    if csv_content:
                        zip_file.writestr(
                            f"{table_name}.csv", csv_content.encode("utf-8")
                        )
                except Exception as e:
                    current_app_logger.error(f"Error exporting {table_name}: {e}")
                    continue

            # Zusätzliche Metadaten-Datei
            metadata = generate_export_metadata()
            zip_file.writestr("export_metadata.txt", metadata.encode("utf-8"))

        zip_buffer.seek(0)

        # ZIP-Datei zurücksenden
        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name=f"printhub_export_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mimetype="application/zip",
        )

    except Exception as e:
        current_app_logger.error(f"Error creating export ZIP: {e}")
        flash("Fehler beim Erstellen der Export-Datei.", "error")
        return redirect(url_for("PrintHub.printHub_export_import"))


def export_single_table(table_name, include_archived=True, include_inactive=True):
    """Exportiert eine einzelne Tabelle als CSV"""
    try:
        export_functions = {
            "filaments": lambda: export_filaments_csv(current_user.username),
            "printers": lambda: export_printers_csv(current_user.username),
            "energy_costs": lambda: export_energy_costs_csv(
                current_user.username, include_inactive
            ),
            "work_hours": lambda: export_work_hours_csv(current_user.username),
            "overhead_profiles": lambda: export_overhead_profiles_csv(
                current_user.username, include_inactive
            ),
            "discount_profiles": lambda: export_discount_profiles_csv(
                current_user.username, include_inactive
            ),
            "quotes": lambda: export_quotes_csv(
                current_user.username, include_archived
            ),
            "suborders": lambda: export_suborders_csv(
                current_user.username, include_archived
            ),
        }

        if table_name not in export_functions:
            flash("Ungültiger Tabellentyp für Export.", "error")
            return redirect(url_for("PrintHub.printHub_export_import"))

        csv_content = export_functions[table_name]()

        if not csv_content:
            flash(f"Keine Daten für {table_name} zum Exportieren gefunden.", "warning")
            return redirect(url_for("PrintHub.printHub_export_import"))

        # CSV-Datei erstellen und zurücksenden
        output = io.BytesIO()
        output.write(csv_content.encode("utf-8"))
        output.seek(0)

        return send_file(
            output,
            as_attachment=True,
            download_name=f"printhub_{table_name}_{current_user.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mimetype="text/csv",
        )

    except Exception as e:
        current_app_logger.error(f"Error exporting {table_name}: {e}")
        flash(f"Fehler beim Export von {table_name}.", "error")
        return redirect(url_for("PrintHub.printHub_export_import"))


# Export-Funktionen für einzelne Tabellen


def export_filaments_csv(username):
    """Exportiert Filamente als CSV"""
    filaments = PrintHubFilament.get_by_user(username)
    if not filaments:
        return None

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "id",
            "filament_type",
            "name",
            "manufacturer",
            "weight",
            "price",
            "notes",
            "created_at",
            "updated_at",
        ]
    )

    # Daten
    for filament in filaments:
        writer.writerow(
            [
                filament.id,
                filament.filament_type,
                filament.name,
                filament.manufacturer,
                filament.weight,
                float(filament.price),
                filament.notes or "",
                filament.created_at.isoformat() if filament.created_at else "",
                filament.updated_at.isoformat() if filament.updated_at else "",
            ]
        )

    return output.getvalue()


def export_printers_csv(username):
    """Exportiert Drucker als CSV"""
    printers = PrintHubPrinter.get_by_user(username)
    if not printers:
        return None

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "id",
            "name",
            "brand",
            "machine_cost_per_hour",
            "energy_consumption",
            "notes",
            "created_at",
            "updated_at",
        ]
    )

    # Daten
    for printer in printers:
        writer.writerow(
            [
                printer.id,
                printer.name,
                printer.brand,
                float(printer.machine_cost_per_hour),
                printer.energy_consumption or "",
                printer.notes or "",
                printer.created_at.isoformat() if printer.created_at else "",
                printer.updated_at.isoformat() if printer.updated_at else "",
            ]
        )

    return output.getvalue()


def export_energy_costs_csv(username, include_inactive=True):
    """Exportiert Energiekosten als CSV"""
    energy_costs = PrintHubEnergyCost.get_by_user(
        username, include_inactive=include_inactive
    )
    if not energy_costs:
        return None

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "id",
            "name",
            "provider",
            "cost_per_kwh",
            "base_fee_monthly",
            "tariff_type",
            "valid_from",
            "valid_until",
            "night_rate",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
    )

    # Daten
    for energy in energy_costs:
        writer.writerow(
            [
                energy.id,
                energy.name,
                energy.provider,
                float(energy.cost_per_kwh),
                float(energy.base_fee_monthly) if energy.base_fee_monthly else "",
                energy.tariff_type or "",
                energy.valid_from.isoformat() if energy.valid_from else "",
                energy.valid_until.isoformat() if energy.valid_until else "",
                float(energy.night_rate) if energy.night_rate else "",
                energy.is_active,
                energy.notes or "",
                energy.created_at.isoformat() if energy.created_at else "",
                energy.updated_at.isoformat() if energy.updated_at else "",
            ]
        )

    return output.getvalue()


def export_work_hours_csv(username):
    """Exportiert Arbeitszeiten als CSV"""
    work_hours = PrintHubWorkHours.get_by_user(username)
    if not work_hours:
        return None

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["id", "name", "role", "cost_per_hour", "created_at", "updated_at"])

    # Daten
    for work in work_hours:
        writer.writerow(
            [
                work.id,
                work.name,
                work.role,
                float(work.cost_per_hour),
                work.created_at.isoformat() if work.created_at else "",
                work.updated_at.isoformat() if work.updated_at else "",
            ]
        )

    return output.getvalue()


def export_overhead_profiles_csv(username, include_inactive=True):
    """Exportiert Overhead-Profile als CSV"""
    profiles = PrintHubOverheadProfile.get_by_user(
        username, include_inactive=include_inactive
    )
    if not profiles:
        return None

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "id",
            "name",
            "location",
            "rent_monthly",
            "heating_electricity",
            "insurance",
            "internet",
            "software_cost",
            "software_billing",
            "other_costs",
            "planned_hours_monthly",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
    )

    # Daten
    for profile in profiles:
        writer.writerow(
            [
                profile.id,
                profile.name,
                profile.location or "",
                float(profile.rent_monthly),
                float(profile.heating_electricity),
                float(profile.insurance),
                float(profile.internet),
                float(profile.software_cost),
                profile.software_billing,
                float(profile.other_costs),
                profile.planned_hours_monthly,
                profile.is_active,
                profile.notes or "",
                profile.created_at.isoformat() if profile.created_at else "",
                profile.updated_at.isoformat() if profile.updated_at else "",
            ]
        )

    return output.getvalue()


def export_discount_profiles_csv(username, include_inactive=True):
    """Exportiert Rabatt-Profile als CSV"""
    profiles = PrintHubDiscountProfile.get_by_user(
        username, include_inactive=include_inactive
    )
    if not profiles:
        return None

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "id",
            "name",
            "discount_type",
            "percentage",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
    )

    # Daten
    for profile in profiles:
        writer.writerow(
            [
                profile.id,
                profile.name,
                profile.discount_type,
                float(profile.percentage),
                profile.is_active,
                profile.notes or "",
                profile.created_at.isoformat() if profile.created_at else "",
                profile.updated_at.isoformat() if profile.updated_at else "",
            ]
        )

    return output.getvalue()


def export_quotes_csv(username, include_archived=True):
    """Exportiert Offerten als CSV"""
    quotes = PrintHubQuote.get_by_user(username, include_archived=include_archived)
    if not quotes:
        return None

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "id",
            "order_name",
            "customer_name",
            "status",
            "is_archived",
            "total_cost",
            "total_time",
            "total_work_time",
            "total_machine_cost",
            "total_material_cost",
            "total_energy_cost",
            "total_work_cost",
            "total_overhead_cost",
            "global_printer_id",
            "global_energy_profile_id",
            "global_work_profile_id",
            "global_overhead_profile_id",
            "global_discount_profile_id",
            "created_at",
            "updated_at",
        ]
    )

    # Daten
    for quote in quotes:
        writer.writerow(
            [
                quote.id,
                quote.order_name,
                quote.customer_name or "",
                quote.status,
                quote.is_archived,
                float(quote.total_cost),
                float(quote.total_time),
                float(quote.total_work_time),
                float(quote.total_machine_cost),
                float(quote.total_material_cost),
                float(quote.total_energy_cost),
                float(quote.total_work_cost),
                float(quote.total_overhead_cost),
                quote.global_printer_id or "",
                quote.global_energy_profile_id or "",
                quote.global_work_profile_id or "",
                quote.global_overhead_profile_id or "",
                quote.global_discount_profile_id or "",
                quote.created_at.isoformat() if quote.created_at else "",
                quote.updated_at.isoformat() if quote.updated_at else "",
            ]
        )

    return output.getvalue()


def export_suborders_csv(username, include_archived=True):
    """Exportiert SubOrders als CSV"""
    quotes = PrintHubQuote.get_by_user(username, include_archived=include_archived)
    if not quotes:
        return None

    suborders = []
    for quote in quotes:
        suborders.extend(quote.suborders)

    if not suborders:
        return None

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        [
            "id",
            "quote_id",
            "name",
            "filament_id",
            "filament_usage_grams",
            "print_time_hours",
            "work_time_hours",
            "printer_id",
            "energy_profile_id",
            "work_profile_id",
            "overhead_profile_id",
            "machine_cost",
            "material_cost",
            "energy_cost",
            "work_cost",
            "overhead_cost",
            "suborder_total",
            "printer_name",
            "filament_name",
            "printer_cost_per_hour",
            "energy_cost_per_kwh",
            "work_cost_per_hour",
            "overhead_cost_per_hour",
        ]
    )

    # Daten
    for suborder in suborders:
        writer.writerow(
            [
                suborder.id,
                suborder.quote_id,
                suborder.name,
                suborder.filament_id,
                suborder.filament_usage_grams,
                float(suborder.print_time_hours),
                float(suborder.work_time_hours),
                suborder.printer_id or "",
                suborder.energy_profile_id or "",
                suborder.work_profile_id or "",
                suborder.overhead_profile_id or "",
                float(suborder.machine_cost),
                float(suborder.material_cost),
                float(suborder.energy_cost),
                float(suborder.work_cost),
                float(suborder.overhead_cost),
                float(suborder.suborder_total),
                suborder.printer_name or "",
                suborder.filament_name or "",
                float(suborder.printer_cost_per_hour),
                float(suborder.energy_cost_per_kwh),
                float(suborder.work_cost_per_hour),
                float(suborder.overhead_cost_per_hour),
            ]
        )

    return output.getvalue()


def generate_export_metadata():
    """Generiert Metadaten für den Export"""
    stats = get_export_stats(current_user.username)

    metadata = f"""PrintHub Datenexport
===================

Benutzer: {current_user.username}
Export-Zeitpunkt: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
PrintHub Version: 0.0.0

Exportierte Datensätze:
- Filamente: {stats['filaments']}
- Drucker: {stats['printers']}
- Energiekosten: {stats['energy_costs']}
- Arbeitszeiten: {stats['work_hours']}
- Overhead-Profile: {stats['overhead_profiles']}
- Rabatt-Profile: {stats['discount_profiles']}
- Offerten: {stats['quotes']}
- Subaufträge: {stats['suborders']}

Gesamt: {stats['total_records']} Datensätze

Hinweise:
- Alle Datums- und Zeitangaben sind im ISO-Format (YYYY-MM-DD bzw. YYYY-MM-DDTHH:MM:SS)
- Dezimalzahlen verwenden Punkt als Dezimaltrennzeichen
- Leere Felder sind als leere Strings exportiert
- Boolean-Werte sind als True/False exportiert
"""

    return metadata


def handle_import_request():
    """Verarbeitet Import-Anfragen"""
    try:
        if "import_file" not in request.files:
            flash("Keine Datei ausgewählt.", "error")
            return redirect(url_for("PrintHub.printHub_export_import"))

        file = request.files["import_file"]
        if file.filename == "":
            flash("Keine Datei ausgewählt.", "error")
            return redirect(url_for("PrintHub.printHub_export_import"))

        overwrite_existing = request.form.get("overwrite_existing") == "on"
        import_type = request.form.get("import_type", "auto")

        filename = secure_filename(file.filename)

        if filename.endswith(".zip"):
            return handle_zip_import(file, overwrite_existing)
        elif filename.endswith(".csv"):
            return handle_csv_import(file, import_type, overwrite_existing)
        else:
            flash(
                "Ungültiges Dateiformat. Nur ZIP und CSV-Dateien sind erlaubt.", "error"
            )
            return redirect(url_for("PrintHub.printHub_export_import"))

    except Exception as e:
        flash(f"Fehler beim Import: {str(e)}", "error")
        current_app_logger.error(f"Import error: {e}")
        return redirect(url_for("PrintHub.printHub_export_import"))


def handle_zip_import(file, overwrite_existing):
    """Verarbeitet ZIP-Import"""
    try:
        # ZIP-Datei direkt aus dem Upload-Stream lesen
        zip_content = io.BytesIO(file.read())

        with zipfile.ZipFile(zip_content, "r") as zip_file:
            # Alle CSV-Dateien importieren
            imported_tables = []
            errors = []

            # Liste der Dateien in der ZIP
            file_list = zip_file.namelist()
            csv_files = [f for f in file_list if f.endswith(".csv")]

            for csv_filename in csv_files:
                table_name = csv_filename.replace(".csv", "")

                try:
                    # CSV-Inhalt aus ZIP lesen
                    with zip_file.open(csv_filename) as csv_file:
                        csv_content = csv_file.read().decode("utf-8")
                        csv_io = io.StringIO(csv_content)

                        result = import_csv_data(csv_io, table_name, overwrite_existing)
                        if result["success"]:
                            imported_tables.append(
                                f"{table_name}: {result['imported']} Datensätze"
                            )
                        else:
                            errors.append(f"{table_name}: {result['error']}")
                except Exception as e:
                    errors.append(f"{table_name}: {str(e)}")

            if imported_tables:
                flash(f"Import erfolgreich: {', '.join(imported_tables)}", "success")

            if errors:
                flash(f"Import-Fehler: {', '.join(errors)}", "warning")

            return redirect(url_for("PrintHub.printHub_export_import"))

    except Exception as e:
        current_app_logger.error(f"ZIP import error: {e}")
        flash(f"Fehler beim ZIP-Import: {str(e)}", "error")
        return redirect(url_for("PrintHub.printHub_export_import"))


def handle_csv_import(file, import_type, overwrite_existing):
    """Verarbeitet CSV-Import"""
    try:
        # Tabellentyp aus Dateiname ermitteln, falls auto
        if import_type == "auto":
            filename = secure_filename(file.filename)
            for table_name in [
                "filaments",
                "printers",
                "energy_costs",
                "work_hours",
                "overhead_profiles",
                "discount_profiles",
                "quotes",
                "suborders",
            ]:
                if table_name in filename.lower():
                    import_type = table_name
                    break

            if import_type == "auto":
                flash(
                    "Tabellentyp konnte nicht automatisch erkannt werden. Bitte manuell auswählen.",
                    "error",
                )
                return redirect(url_for("PrintHub.printHub_export_import"))

        # CSV-Inhalt lesen
        file.seek(0)
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")

        # StringIO-Object für CSV-Import erstellen
        csv_io = io.StringIO(content)

        result = import_csv_data(csv_io, import_type, overwrite_existing)

        if result["success"]:
            flash(
                f"Import erfolgreich: {result['imported']} {import_type} importiert.",
                "success",
            )
        else:
            flash(f"Import-Fehler: {result['error']}", "error")

        return redirect(url_for("PrintHub.printHub_export_import"))

    except Exception as e:
        current_app_logger.error(f"CSV import error: {e}")
        flash(f"Fehler beim CSV-Import: {str(e)}", "error")
        return redirect(url_for("PrintHub.printHub_export_import"))


def import_csv_data(file_obj, table_name, overwrite_existing=False):
    """Importiert CSV-Daten in die entsprechende Tabelle"""
    try:
        # CSV lesen - file_obj kann FileUpload oder StringIO sein
        if hasattr(file_obj, "read"):
            # File Upload Object
            file_obj.seek(0)
            content = file_obj.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8")
        else:
            # StringIO Object
            content = file_obj.getvalue()

        csv_reader = csv.DictReader(io.StringIO(content))

        import_functions = {
            "filaments": import_filaments_from_csv,
            "printers": import_printers_from_csv,
            "energy_costs": import_energy_costs_from_csv,
            "work_hours": import_work_hours_from_csv,
            "overhead_profiles": import_overhead_profiles_from_csv,
            "discount_profiles": import_discount_profiles_from_csv,
            "quotes": import_quotes_from_csv,
            "suborders": import_suborders_from_csv,
        }

        if table_name not in import_functions:
            return {"success": False, "error": f"Unbekannter Tabellentyp: {table_name}"}

        return import_functions[table_name](csv_reader, overwrite_existing)

    except Exception as e:
        current_app_logger.error(f"CSV data import error: {e}")
        return {"success": False, "error": str(e)}


# Import-Funktionen für einzelne Tabellen (vereinfacht dargestellt)


def import_filaments_from_csv(csv_reader, overwrite_existing):
    """Importiert Filamente aus CSV"""
    try:
        imported_count = 0

        for row in csv_reader:
            # Überprüfen ob Datensatz bereits existiert (nach name + manufacturer)
            existing = PrintHubFilament.query.filter_by(
                name=row["name"],
                manufacturer=row["manufacturer"],
                created_by=current_user.username,
            ).first()

            if existing and not overwrite_existing:
                continue

            if existing and overwrite_existing:
                # Update existing
                existing.filament_type = row["filament_type"]
                existing.weight = int(row["weight"])
                existing.price = float(row["price"])
                existing.notes = row["notes"] if row["notes"] else None
                existing.updated_at = get_current_time()
            else:
                # Create new
                new_filament = PrintHubFilament(
                    filament_type=row["filament_type"],
                    name=row["name"],
                    manufacturer=row["manufacturer"],
                    weight=int(row["weight"]),
                    price=float(row["price"]),
                    notes=row["notes"] if row["notes"] else None,
                    created_by=current_user.username,
                    created_at=get_current_time(),
                    updated_at=get_current_time(),
                )
                db.session.add(new_filament)

            imported_count += 1

        db.session.commit()
        return {"success": True, "imported": imported_count}

    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}


# Die anderen Import-Funktionen folgen dem gleichen Muster...
# (Aus Platzgründen verkürzt, aber vollständig implementierbar)


def import_printers_from_csv(csv_reader, overwrite_existing):
    """Importiert Drucker aus CSV"""
    # Ähnliche Implementierung wie import_filaments_from_csv
    try:
        imported_count = 0

        for row in csv_reader:
            existing = PrintHubPrinter.query.filter_by(
                name=row["name"], created_by=current_user.username
            ).first()

            if existing and not overwrite_existing:
                continue

            if existing and overwrite_existing:
                existing.brand = row["brand"]
                existing.machine_cost_per_hour = float(row["machine_cost_per_hour"])
                existing.energy_consumption = (
                    int(row["energy_consumption"])
                    if row["energy_consumption"]
                    else None
                )
                existing.notes = row["notes"] if row["notes"] else None
                existing.updated_at = get_current_time()
            else:
                new_printer = PrintHubPrinter(
                    name=row["name"],
                    brand=row["brand"],
                    machine_cost_per_hour=float(row["machine_cost_per_hour"]),
                    energy_consumption=(
                        int(row["energy_consumption"])
                        if row["energy_consumption"]
                        else None
                    ),
                    notes=row["notes"] if row["notes"] else None,
                    created_by=current_user.username,
                )
                db.session.add(new_printer)

            imported_count += 1

        db.session.commit()
        return {"success": True, "imported": imported_count}

    except Exception as e:
        db.session.rollback()
        return {"success": False, "error": str(e)}


# Placeholder-Implementierungen für die anderen Import-Funktionen
def import_energy_costs_from_csv(csv_reader, overwrite_existing):
    return {
        "success": False,
        "error": "Import für Energiekosten noch nicht implementiert",
    }


def import_work_hours_from_csv(csv_reader, overwrite_existing):
    return {
        "success": False,
        "error": "Import für Arbeitszeiten noch nicht implementiert",
    }


def import_overhead_profiles_from_csv(csv_reader, overwrite_existing):
    return {
        "success": False,
        "error": "Import für Overhead-Profile noch nicht implementiert",
    }


def import_discount_profiles_from_csv(csv_reader, overwrite_existing):
    return {
        "success": False,
        "error": "Import für Rabatt-Profile noch nicht implementiert",
    }


def import_quotes_from_csv(csv_reader, overwrite_existing):
    return {"success": False, "error": "Import für Offerten noch nicht implementiert"}


def import_suborders_from_csv(csv_reader, overwrite_existing):
    return {
        "success": False,
        "error": "Import für Subaufträge noch nicht implementiert",
    }


app_logger.info("Ende App-PrintHub Route Initialization")
